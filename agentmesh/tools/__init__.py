# Import base tool
from agentmesh.tools.base_tool import BaseTool
from agentmesh.tools.tool_manager import ToolManager

# Import specific tools
from agentmesh.tools.google_search.google_search import GoogleSearch
from agentmesh.tools.calculator.calculator import Calculator
from agentmesh.tools.current_time.current_time import CurrentTime
from agentmesh.tools.file_output.file_output import FileOutput

# 延迟导入 BrowserTool
def _import_browser_tool():
    try:
        from agentmesh.tools.browser.browser_tool import BrowserTool
        return BrowserTool
    except ImportError:
        # 返回一个占位符类，在实例化时会提示用户安装依赖
        class BrowserToolPlaceholder:
            def __init__(self, *args, **kwargs):
                raise ImportError(
                    "The 'browser-use' package is required to use BrowserTool. "
                    "Please install it with 'pip install browser-use>=0.1.40' or "
                    "'pip install agentmesh-sdk[full]'."
                )
        return BrowserToolPlaceholder

# 动态设置 BrowserTool
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
