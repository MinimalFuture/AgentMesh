import importlib
from pathlib import Path
from typing import Dict
from agentmesh.tools.base_tool import BaseTool
from agentmesh.common import config


class ToolManager:
    """
    A manager for loading and accessing tools.
    """
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance of ToolManager exists."""
        if cls._instance is None:
            cls._instance = super(ToolManager, cls).__new__(cls)
            cls._instance.tools = {}
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        # Initialize only once
        if not hasattr(self, 'tools'):
            self.tools: Dict[str, BaseTool] = {}
    
    def load_tools(self, tools_dir: str = "agentmesh/tools"):
        """
        Load tools from both directory and configuration.
        
        :param tools_dir: Directory to scan for tool modules
        """
        # First, load tools from directory (for backward compatibility)
        self._load_tools_from_directory(tools_dir)
        
        # Then, configure tools from config file
        self._configure_tools_from_config()
        
        # print(f"Loaded {len(self.tools)} tools: {', '.join(self.tools.keys())}")
    
    def _load_tools_from_directory(self, tools_dir: str):
        """Dynamically load tools from directory"""
        tools_path = Path(tools_dir)
        for py_file in tools_path.rglob("*.py"):  # Use rglob to recursively find .py files
            if py_file.name in ["__init__.py", "base_tool.py", "tool_manager.py"]:
                continue
            
            # Construct the module name based on the relative path
            plugin_name = py_file.stem
            module_name = str(py_file.relative_to(Path(tools_dir).parent)).replace("/", ".").replace(".py", "")
            # print(f"plugin_name: {plugin_name}, module_name: {module_name}")
            
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
                    try:
                        tool_instance = cls()
                        self.tools[tool_instance.name] = tool_instance
                    except TypeError as e:
                        print(f"Error initializing tool {cls.__name__}: {e}")
    
    def _configure_tools_from_config(self):
        """Configure tools based on configuration file"""
        try:
            # Get tools configuration
            tools_config = config().get("tools", {})
            
            # Update tool configurations if they exist
            for tool_name, tool_config in tools_config.items():
                if tool_name in self.tools:
                    self.tools[tool_name].config = tool_config
        except Exception as e:
            print(f"Error configuring tools from config: {e}")
    
    def get_tool(self, name: str) -> BaseTool:
        """
        Get a tool by name.
        
        :param name: The name of the tool to get.
        :return: The tool instance or None if not found.
        """
        return self.tools.get(name)
    
    def list_tools(self) -> dict:
        """
        Get information about all loaded tools.
        
        :return: A dictionary with tool information.
        """
        return {
            name: {
                "description": tool.description,
                "parameters": tool.get_json_schema()
            }
            for name, tool in self.tools.items()
        }
