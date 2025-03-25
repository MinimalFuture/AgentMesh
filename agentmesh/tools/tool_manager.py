import importlib
from pathlib import Path
from typing import Dict
from agentmesh.tools.base_tool import BaseTool


class ToolManager:
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
    
    def load_tools(self, tools_dir: str = "agentmesh/tools"):
        # Dynamically load tools from directory
        tools_path = Path(tools_dir)
        for py_file in tools_path.rglob("*.py"):  # Use rglob to recursively find .py files
            if py_file.name in ["__init__.py", "base_tool.py", "tool_manager.py"]:
                continue
            
            # Construct the module name based on the relative path
            plugin_name = py_file.stem
            module_name = str(py_file.relative_to(Path(tools_dir).parent)).replace("/", ".").replace(".py", "")
            print(f"plugin_name: {plugin_name}, module_name: {module_name}")
            
            # Import using the corrected module name
            try:
                module = importlib.import_module(f"agentmesh.{module_name}")  # Ensure the correct base package
            except ModuleNotFoundError as e:
                print(f"Error importing module {module_name}: {e}")
                continue
            
            for attr_name in dir(module):
                cls = getattr(module, attr_name)
                if (
                    isinstance(cls, type) 
                    and issubclass(cls, BaseTool) 
                    and cls != BaseTool
                ):
                    tool_instance = cls()
                    self.tools[tool_instance.name] = tool_instance
        print(self.list_tools())

    def get_tool(self, name: str) -> BaseTool:
        return self.tools.get(name)
    
    def list_tools(self) -> dict:
        return {
            name: {
                "description": tool.description,
                "parameters": tool.get_json_schema()
            }
            for name, tool in self.tools.items()
        }
