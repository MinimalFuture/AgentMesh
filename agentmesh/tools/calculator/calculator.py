import math
from agentmesh.tools.base_tool import BaseTool


class Calculator(BaseTool):
    name: str = "calculator"
    description: str = "A tool to perform basic mathematical calculations."
    args_schema: dict = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression to evaluate (e.g., '2 + 2', '5 * 3', 'sqrt(16)'). "
                               "Ensure your input is a valid Python expression, it will be evaluated directly."
            }
        },
        "required": ["expression"]
    }
    config: dict = {}

    def run(self, args: dict) -> dict:
        try:
            # Get the expression
            expression = args["expression"]
            
            # Create a safe local environment containing only basic math functions
            safe_locals = {
                "abs": abs,
                "round": round,
                "max": max,
                "min": min,
                "pow": pow,
                "sqrt": math.sqrt,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "pi": math.pi,
                "e": math.e,
                "log": math.log,
                "log10": math.log10,
                "exp": math.exp,
                "floor": math.floor,
                "ceil": math.ceil
            }
            
            # Safely evaluate the expression
            result = eval(expression, {"__builtins__": {}}, safe_locals)
            
            return {
                "result": result,
                "expression": expression
            }
        except Exception as e:
            return {
                "error": str(e),
                "expression": args.get("expression", "")
            }
