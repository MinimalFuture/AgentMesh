import os
import time
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional

from agentmesh.tools.base_tool import BaseTool, ToolResult
from agentmesh.common import config


class FileOutput(BaseTool):
    """Tool for saving content to files in the workspace directory."""
    
    name = "file_output"
    description = "Save content to a file in the workspace directory."
    params = {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "The content to save to the file."
            },
            "file_name": {
                "type": "string",
                "description": "Optional. The name of the file to save. If not provided, a name will be generated based on the content."
            },
            "file_type": {
                "type": "string",
                "description": "Optional. The type/extension of the file (e.g., 'txt', 'md', 'py', 'java'). If not provided, it will be inferred from the content."
            },
            "team_name": {
                "type": "string",
                "description": "Optional. The name of the team. Used for organizing files in the workspace."
            },
            "task_id": {
                "type": "string",
                "description": "Optional. The ID of the current task. Used for organizing files in the workspace."
            }
        },
        "required": ["content"]
    }
    
    def __init__(self):
        self.config = {}
        self.workspace_dir = Path("workspace")
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        """
        Save content to a file in the workspace directory.
        
        :param params: The parameters for the file output operation.
        :return: Result of the operation.
        """
        # Extract parameters
        content = params.get("content", "")
        if not content:
            return ToolResult.fail("Error: No content provided.")
        
        file_name = params.get("file_name")
        file_type = params.get("file_type")
        team_name = params.get("team_name", "default_team")
        task_id = params.get("task_id")
        
        # If task_id is not provided, generate one based on timestamp
        if not task_id:
            task_id = f"task_{int(time.time())}"
        
        # Create directory structure
        task_dir = self.workspace_dir / team_name / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        
        # If file_name is not provided, try to infer it from content
        if not file_name:
            file_name = self._infer_file_name(content)
        
        # If file_type is not provided, try to infer it from content
        if not file_type:
            file_type = self._infer_file_type(content)
        
        # Ensure file_name has the correct extension
        if file_type and not file_name.endswith(f".{file_type}"):
            file_name = f"{file_name}.{file_type}"
        
        # Create the full file path
        file_path = task_dir / file_name
        
        try:
            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return ToolResult.success({
                "file_path": str(file_path),
                "file_name": file_name,
                "file_type": file_type,
                "size": len(content),
                "message": f"Content successfully saved to {file_path}"
            })
        
        except Exception as e:
            return ToolResult.fail(f"Error saving file: {str(e)}")
    
    def _infer_file_name(self, content: str) -> str:
        """
        Infer a file name from the content.
        
        :param content: The content to analyze.
        :return: A suggested file name.
        """
        # Check for title patterns in markdown
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            # Convert title to a valid filename
            title = title_match.group(1).strip()
            return self._sanitize_filename(title)
        
        # Check for class/function definitions in code
        code_match = re.search(r'(class|def|function)\s+(\w+)', content)
        if code_match:
            return self._sanitize_filename(code_match.group(2))
        
        # Default name based on content type
        if self._is_likely_code(content):
            return "code"
        elif self._is_likely_markdown(content):
            return "document"
        elif self._is_likely_json(content):
            return "data"
        else:
            return "output"
    
    def _infer_file_type(self, content: str) -> str:
        """
        Infer the file type/extension from the content.
        
        :param content: The content to analyze.
        :return: A suggested file extension.
        """
        # Check for common programming language patterns
        if re.search(r'(import\s+[a-zA-Z0-9_]+|from\s+[a-zA-Z0-9_\.]+\s+import)', content):
            return "py"  # Python
        elif re.search(r'(public\s+class|private\s+class|protected\s+class)', content):
            return "java"  # Java
        elif re.search(r'(function\s+\w+\s*\(|const\s+\w+\s*=|let\s+\w+\s*=|var\s+\w+\s*=)', content):
            return "js"  # JavaScript
        elif re.search(r'(<html|<body|<div|<p>)', content):
            return "html"  # HTML
        elif re.search(r'(#include\s+<\w+\.h>|int\s+main\s*\()', content):
            return "cpp"  # C/C++
        
        # Check for markdown
        if self._is_likely_markdown(content):
            return "md"
        
        # Check for JSON
        if self._is_likely_json(content):
            return "json"
        
        # Default to text
        return "txt"
    
    def _is_likely_code(self, content: str) -> bool:
        """Check if the content is likely code."""
        code_patterns = [
            r'(class|def|function|import|from|public|private|protected|#include)',
            r'(\{\s*\n|\}\s*\n|\[\s*\n|\]\s*\n)',
            r'(if\s*\(|for\s*\(|while\s*\()'
        ]
        return any(re.search(pattern, content) for pattern in code_patterns)
    
    def _is_likely_markdown(self, content: str) -> bool:
        """Check if the content is likely markdown."""
        md_patterns = [
            r'^#\s+.+$',  # Headers
            r'^\*\s+.+$',  # Unordered lists
            r'^\d+\.\s+.+$',  # Ordered lists
            r'\[.+\]\(.+\)',  # Links
            r'!\[.+\]\(.+\)'  # Images
        ]
        return any(re.search(pattern, content, re.MULTILINE) for pattern in md_patterns)
    
    def _is_likely_json(self, content: str) -> bool:
        """Check if the content is likely JSON."""
        try:
            content = content.strip()
            if (content.startswith('{') and content.endswith('}')) or (content.startswith('[') and content.endswith(']')):
                json.loads(content)
                return True
        except:
            pass
        return False
    
    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize a string to be used as a filename.
        
        :param name: The string to sanitize.
        :return: A sanitized filename.
        """
        # Replace spaces with underscores
        name = name.replace(' ', '_')
        
        # Remove invalid characters
        name = re.sub(r'[^\w\-\.]', '', name)
        
        # Limit length
        if len(name) > 50:
            name = name[:50]
        
        return name.lower() 