from typing import Any


class BaseTool:
    # Class attributes must be inherited
    name: str = "base_tool"
    description: str = "Base tool"
    args_schema: dict = {}  # Store JSON Schema

    @classmethod
    def get_json_schema(cls) -> dict:
        """Get the standard description of the tool"""
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": cls.args_schema
        }

    def execute(self, args: dict) -> Any:
        try:
            return self.run(args)
        except Exception as e:
            print(e)

    def run(self, args: dict) -> Any:
        """Specific logic to be implemented by subclasses"""
        raise NotImplementedError

    @classmethod
    def _parse_schema(cls) -> dict:
        """Convert JSON Schema to Pydantic fields"""
        fields = {}
        for name, prop in cls.args_schema["properties"].items():
            # Convert JSON Schema types to Python types
            type_map = {
                "string": str,
                "number": float,
                "integer": int,
                "boolean": bool,
                "array": list,
                "object": dict
            }
            fields[name] = (
                type_map[prop["type"]],
                prop.get("default", ...)
            )
        return fields
