# Import base tool
from agentmesh.tools.base_tool import BaseTool
from agentmesh.tools.tool_manager import ToolManager

# Import specific tools
from agentmesh.tools.google_search.google_search import GoogleSearch
from agentmesh.tools.parallel_search.parallel_search import ParallelSearch
from agentmesh.tools.calculator.calculator import Calculator
from agentmesh.tools.current_time.current_time import CurrentTime
from agentmesh.tools.file_save.file_save import FileSave
from agentmesh.tools.terminal.terminal import Terminal

# Import new file operation tools
from agentmesh.tools.read.read import Read
from agentmesh.tools.write.write import Write
from agentmesh.tools.edit.edit import Edit
from agentmesh.tools.bash.bash import Bash
from agentmesh.tools.grep.grep import Grep
from agentmesh.tools.find.find import Find
from agentmesh.tools.ls.ls import Ls

# Import memory tools
from agentmesh.tools.memory.memory_search import MemorySearchTool
from agentmesh.tools.memory.memory_get import MemoryGetTool


# Delayed import for BrowserTool
def _import_browser_tool():
    try:
        from agentmesh.tools.browser.browser_tool import BrowserTool
        return BrowserTool
    except ImportError:
        # Return a placeholder class that will prompt the user to install dependencies when instantiated
        class BrowserToolPlaceholder:
            def __init__(self, *args, **kwargs):
                raise ImportError(
                    "The 'browser-use' package is required to use BrowserTool. "
                    "Please install it with 'pip install browser-use>=0.1.40' or "
                    "'pip install agentmesh-sdk[full]'."
                )

        return BrowserToolPlaceholder


# Dynamically set BrowserTool
BrowserTool = _import_browser_tool()

# Export all tools
__all__ = [
    'BaseTool',
    'ToolManager',
    'GoogleSearch',
    'ParallelSearch',
    'Calculator',
    'CurrentTime',
    'FileSave',
    'BrowserTool',
    'Terminal',
    # New file operation tools
    'Read',
    'Write',
    'Edit',
    'Bash',
    'Grep',
    'Find',
    'Ls',
    # Memory tools
    'MemorySearchTool',
    'MemoryGetTool'
]

"""
Tools module for AgentMesh.
"""
