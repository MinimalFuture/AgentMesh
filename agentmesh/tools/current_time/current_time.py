import datetime
import time
from agentmesh.tools.base_tool import BaseTool


class CurrentTime(BaseTool):
    name: str = "time"
    description: str = "A tool to get current date and time information."
    args_schema: dict = {
        "type": "object",
        "properties": {
            "format": {
                "type": "string",
                "description": "Optional format for the time (e.g., 'iso', 'unix', 'human'). Default is 'human'."
            },
            "timezone": {
                "type": "string",
                "description": "Optional timezone specification (e.g., 'UTC', 'local'). Default is 'local'."
            }
        },
        "required": []
    }
    config: dict = {}

    def run(self, args: dict) -> dict:
        try:
            # Get the format and timezone parameters, with defaults
            time_format = args.get("format", "human").lower()
            timezone = args.get("timezone", "local").lower()
            
            # Get current time
            current_time = datetime.datetime.now()
            
            # Handle timezone if specified
            if timezone == "utc":
                current_time = datetime.datetime.utcnow()
            
            # Format the time according to the specified format
            if time_format == "iso":
                # ISO 8601 format
                formatted_time = current_time.isoformat()
            elif time_format == "unix":
                # Unix timestamp (seconds since epoch)
                formatted_time = time.time()
            else:
                # Human-readable format
                formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Prepare additional time components for the response
            year = current_time.year
            month = current_time.month
            day = current_time.day
            hour = current_time.hour
            minute = current_time.minute
            second = current_time.second
            weekday = current_time.strftime("%A")  # Full weekday name
            
            return {
                "current_time": formatted_time,
                "components": {
                    "year": year,
                    "month": month,
                    "day": day,
                    "hour": hour,
                    "minute": minute,
                    "second": second,
                    "weekday": weekday
                },
                "format": time_format,
                "timezone": timezone
            }
        except Exception as e:
            print(e)

            return {
                "error": str(e)
            }
