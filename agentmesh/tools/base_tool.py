from typing import Any
from pydantic import BaseModel, Field
from agentmesh.models.llm.base_model import LLMModel
from agentmesh.common import logger


class ToolResult(BaseModel):
    status: str = Field(default=None)
    result: Any = Field(default=None)
    ext_data: Any = Field(default=None)

    @staticmethod
    def success(result, ext_data: Any = None):
        return ToolResult(status="success", result=result, ext_data=ext_data)

    @staticmethod
    def fail(result, ext_data: Any = None):
        return ToolResult(status="error", result=result, ext_data=ext_data)


class BaseTool:
    # Class attributes must be inherited
    name: str = "base_tool"
    description: str = "Base tool"
    params: dict = {}  # Store JSON Schema
    model: LLMModel = None

    @classmethod
    def get_json_schema(cls) -> dict:
        """Get the standard description of the tool"""
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": cls.params
        }

    def execute_tool(self, params: dict) -> ToolResult:
        try:
            return self.execute(params)
        except Exception as e:
            logger.error(e)

    def execute(self, params: dict) -> ToolResult:
        """Specific logic to be implemented by subclasses"""
        raise NotImplementedError

    @classmethod
    def _parse_schema(cls) -> dict:
        """Convert JSON Schema to Pydantic fields"""
        fields = {}
        for name, prop in cls.params["properties"].items():
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
