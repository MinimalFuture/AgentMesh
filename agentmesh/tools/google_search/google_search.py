import requests
from agentmesh.tools.base_tool import BaseTool


class GoogleSearchTool(BaseTool):
    name: str = "google_search"
    description: str = "A tool to perform Google searches using the Serper API."
    args_schema: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to perform."
            }
        },
        "required": ["query"]
    }
    config: dict = {}

    def _run(self, args: dict) -> dict:
        api_key = "YOUR API KEY"  # Replace with your actual API key
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        data = {
            "q": args["query"]
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()  # Return the JSON response from the API
