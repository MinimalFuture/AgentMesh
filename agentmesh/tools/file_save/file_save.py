import os
import time
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from agentmesh.tools.base_tool import BaseTool, ToolResult, ToolStage
from agentmesh.models import LLMRequest
from agentmesh.common.utils.log import logger


class FileSave(BaseTool):
    """Tool for saving content to files in the workspace directory."""

    name = "file_save"
    description = "Save the agent's output to a file in the workspace directory. Content is automatically extracted from the agent's previous outputs."

    # Set as post-process stage tool
    stage = ToolStage.POST_PROCESS

    params = {
        "type": "object",
        "properties": {
            "file_name": {
                "type": "string",
                "description": "Optional. The name of the file to save. If not provided, a name will be generated based on the content."
            },
            "file_type": {
                "type": "string",
                "description": "Optional. The type/extension of the file (e.g., 'txt', 'md', 'py', 'java'). If not provided, it will be inferred from the content."
            },
            "extract_code": {
                "type": "boolean",
                "description": "Optional. If true, will attempt to extract code blocks from the content. Default is false."
            },
            "task_dir": {
                "type": "string",
                "description": "Optional. The name of the task directory. If not provided, it will be generated based on the content."
            }
        },
        "required": []  # No required fields, as everything can be extracted from context
    }

    def __init__(self):
        self.context = None
        self.config = {}
        self.workspace_dir = Path("workspace")

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        """
        Save content to a file in the workspace directory.
        
        :param params: The parameters for the file output operation.
        :return: Result of the operation.
        """
        # Extract content from context
        if not hasattr(self, 'context') or not self.context:
            return ToolResult.fail("Error: No context available to extract content from.")

        content = self._extract_content_from_context()

        # If no content could be extracted, return error
        if not content:
            return ToolResult.fail("Error: Couldn't extract content from context.")

        # Use model to determine file parameters
        try:
            task_dir = self._get_task_dir_from_context()
            file_name, file_type, extract_code = self._get_file_params_from_model(content, params)
        except Exception as e:
            logger.error(f"Error determining file parameters: {str(e)}")
            # Fall back to manual parameter extraction
            task_dir = params.get("task_dir") or self._get_task_id_from_context() or f"task_{int(time.time())}"
            file_name = params.get("file_name") or self._infer_file_name(content)
            file_type = params.get("file_type") or self._infer_file_type(content)
            extract_code = params.get("extract_code", False)

        # If extract_code is True, extract code blocks from content
        if extract_code:
            extracted_content = self._extract_code_blocks(content)
            if extracted_content:
                content = extracted_content

        # Get team_name from context
        team_name = self._get_team_name_from_context() or "default_team"

        # Create directory structure
        task_dir_path = self.workspace_dir / team_name / task_dir
        task_dir_path.mkdir(parents=True, exist_ok=True)

        # Ensure file_name has the correct extension
        if file_type and not file_name.endswith(f".{file_type}"):
            file_name = f"{file_name}.{file_type}"

        # Create the full file path
        file_path = task_dir_path / file_name

        try:
            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return ToolResult.success({
                "file_path": str(file_path),
                "file_name": file_name,
                "file_type": file_type,
                "task_dir": task_dir,
                "size": len(content),
                "message": f"Content successfully saved to {file_path}"
            })

        except Exception as e:
            return ToolResult.fail(f"Error saving file: {str(e)}")

    def _get_file_params_from_model(self, content: str, params: Dict[str, Any]) -> Tuple[str, str, bool]:
        """
        Use the model to determine file parameters based on content.

        :param content: The content to analyze
        :param params: User-provided parameters that may override model decisions
        :return: Tuple of (task_dir, file_name, file_type, extract_code)
        """
        # Use user-provided parameters if available
        if all(key in params for key in ["file_name", "file_type", "extract_code"]):
            return (
                params["file_name"],
                params["file_type"],
                params["extract_code"]
            )

        # Prepare a prompt for the model
        prompt = f"""
Analyze the following content and determine the best file parameters for saving it.
Return your answer in JSON format with the following fields:
- file_name: A descriptive name for the file without extension (use snake_case)
- file_type: The appropriate file extension (e.g., 'py', 'md', 'txt', 'js', 'html', 'css', 'json')
- extract_code: Boolean indicating whether code blocks should be extracted from the content

Content preview (first 1000 characters):
{content[:1000]}
{"..." if len(content) > 1000 else ""}

Return only valid JSON without any additional text.
"""

        # Create a request to the model
        request = LLMRequest(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            json_format=True
        )

        # Use the model to get file parameters
        if not self.model:
            # If no model is available, use default parameters
            logger.warning("No model available for file parameter inference, using defaults")
            return (
                self._infer_file_name(content),
                self._infer_file_type(content),
                self._is_likely_code(content)
            )

        try:
            response = self.model.call(request)

            if response.is_error:
                logger.warning(f"Error from model: {response.error_message}")
                raise Exception(f"Model error: {response.error_message}")

            # Extract JSON from response
            result = response.data["choices"][0]["message"]["content"]

            # Clean up the result to ensure it's valid JSON
            result = result.strip()
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()

            # Parse the JSON
            params_dict = json.loads(result)

            # Extract and validate parameters
            file_name = params_dict.get("file_name", "").strip()
            file_type = params_dict.get("file_type", "").strip()
            extract_code = params_dict.get("extract_code", False)

            # Apply fallbacks for empty values
            if not file_name:
                file_name = self._infer_file_name(content)
            if not file_type:
                file_type = self._infer_file_type(content)

            # Sanitize values
            file_name = self._sanitize_filename(file_name)

            return file_name, file_type, extract_code

        except Exception as e:
            logger.error(f"Error processing model response: {str(e)}")
            # Fall back to default parameters
            return (
                self._infer_file_name(content),
                self._infer_file_type(content),
                self._is_likely_code(content)
            )

    def _get_team_name_from_context(self) -> Optional[str]:
        """
        Get team name from the agent's context.

        :return: Team name or None if not found
        """
        if hasattr(self, 'context') and self.context:
            # Try to get team name from team_context
            if hasattr(self.context, 'team_context') and self.context.team_context:
                return self.context.team_context.name

            # Try direct team_name attribute
            if hasattr(self.context, 'name'):
                return self.context.name

        return None

    def _get_task_id_from_context(self) -> Optional[str]:
        """
        Get task ID from the agent's context.

        :return: Task ID or None if not found
        """
        if hasattr(self, 'context') and self.context:
            # Try to get task ID from task object
            if hasattr(self.context, 'task') and self.context.task:
                return self.context.task.id

            # Try team_context's task
            if hasattr(self.context, 'team_context') and self.context.team_context:
                if hasattr(self.context.team_context, 'task') and self.context.team_context.task:
                    return self.context.team_context.task.id

        return None

    def _get_task_dir_from_context(self) -> Optional[str]:
        """
        Get task directory name from the team context.

        :return: Task directory name or None if not found
        """
        if hasattr(self, 'context') and self.context:
            # Try to get from team_context
            if hasattr(self.context, 'team_context') and self.context.team_context:
                if hasattr(self.context.team_context, 'task_short_name') and self.context.team_context.task_short_name:
                    return self.context.team_context.task_short_name

        # Fall back to task ID if available
        return self._get_task_id_from_context()

    def _extract_content_from_context(self) -> str:
        """
        Extract content from the agent's context.

        :return: Extracted content
        """
        # Check if we have access to the agent's context
        if not hasattr(self, 'context') or not self.context:
            return ""

        # Try to get the most recent final answer from the agent
        if hasattr(self.context, 'final_answer') and self.context.final_answer:
            return self.context.final_answer

        # Try to get the most recent final answer from team context
        if hasattr(self.context, 'team_context') and self.context.team_context:
            if hasattr(self.context.team_context, 'agent_outputs') and self.context.team_context.agent_outputs:
                latest_output = self.context.team_context.agent_outputs[-1].output
                return latest_output

        # If we have action history, try to get the most recent final answer
        if hasattr(self.context, 'action_history') and self.context.action_history:
            for action in reversed(self.context.action_history):
                if "final_answer" in action and action["final_answer"]:
                    return action["final_answer"]

        return ""

    def _extract_code_blocks(self, content: str) -> str:
        """
        Extract code blocks from markdown content.

        :param content: The content to extract code blocks from
        :return: Extracted code blocks
        """
        # Pattern to match markdown code blocks
        code_block_pattern = r'```(?:\w+)?\n([\s\S]*?)\n```'

        # Find all code blocks
        code_blocks = re.findall(code_block_pattern, content)

        if code_blocks:
            # Join all code blocks with newlines
            return '\n\n'.join(code_blocks)

        return content  # Return original content if no code blocks found

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
            if (content.startswith('{') and content.endswith('}')) or (
                    content.startswith('[') and content.endswith(']')):
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
