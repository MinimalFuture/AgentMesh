# Import base tool
from agentmesh.tools.base_tool import BaseTool
from agentmesh.tools.tool_manager import ToolManager

# Import specific tools
from agentmesh.tools.google_search.google_search import GoogleSearch
from agentmesh.tools.calculator.calculator import Calculator
from agentmesh.tools.current_time.current_time import CurrentTime
from agentmesh.tools.file_output.file_output import FileOutput

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
    'Calculator',
    'CurrentTime',
    'FileOutput',
    'BrowserTool'
]

"""
Tools module for AgentMesh.
"""
