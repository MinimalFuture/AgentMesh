import importlib
import importlib.util
from pathlib import Path
from typing import Dict
from agentmesh.tools.base_tool import BaseTool
from agentmesh.common import config
from agentmesh.common.utils.log import logger  # Import the logging module


class ToolManager:
    """
    Tool manager for managing tools.
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
        """Dynamically load tools from directory using file loading"""
        tools_path = Path(tools_dir)

        # Traverse all .py files
        for py_file in tools_path.rglob("*.py"):
            # Skip initialization files and base tool files
            if py_file.name in ["__init__.py", "base_tool.py", "tool_manager.py"]:
                continue

            # Get module name
            module_name = py_file.stem

            try:
                # Load module directly from file
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Find tool classes in the module
                    for attr_name in dir(module):
                        cls = getattr(module, attr_name)
                        if (
                                isinstance(cls, type)
                                and issubclass(cls, BaseTool)
                                and cls != BaseTool
                        ):
                            try:
                                # Instantiate tool and add to tool dictionary
                                tool_instance = cls()
                                self.tools[tool_instance.name] = tool_instance
                            except ImportError as e:
                                # Ignore browser_use dependency missing errors
                                if "browser_use" in str(e):
                                    pass
                                else:
                                    print(f"Error initializing tool {cls.__name__}: {e}")
                            except Exception as e:
                                print(f"Error initializing tool {cls.__name__}: {e}")
            except Exception as e:
                print(f"Error importing module {py_file}: {e}")

    def _configure_tools_from_config(self):
        """Configure tools based on configuration file"""
        try:
            # Get tools configuration
            tools_config = config().get("tools", {})

            # Record tools that are configured but not loaded
            missing_tools = []

            # Update tool configurations if they exist
            for tool_name, tool_config in tools_config.items():
                if tool_name in self.tools:
                    self.tools[tool_name].config = tool_config
                else:
                    # Tool is configured but not successfully loaded
                    missing_tools.append(tool_name)

            # If there are missing tools, record warnings
            if missing_tools:
                for tool_name in missing_tools:
                    if tool_name == "browser":
                        logger.error(
                            "Browser tool is configured but could not be loaded. "
                            "Please install the required dependency with: "
                            "pip install browser-use>=0.1.40 or pip install agentmesh-sdk[full]"
                        )
                    else:
                        logger.warning(f"Tool '{tool_name}' is configured but could not be loaded.")

        except Exception as e:
            logger.error(f"Error configuring tools from config: {e}")

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
