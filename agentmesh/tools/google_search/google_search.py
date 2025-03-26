import requests

from agentmesh.tools.base_tool import BaseTool


class GoogleSearch(BaseTool):
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

    def run(self, args: dict) -> dict:
        api_key = self.config.get("api_key")  # Replace with your actual API key
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        data = {
            "q": args.get("query"),
            "k": 10
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        # Check if the returned result contains the 'organic' key and ensure it is a list
        if 'organic' in result and isinstance(result.get('organic'), list):
            return result['organic']
        else:
            # If there are no organic results, return the full response or an empty list
            return result.get('organic', []) if isinstance(result.get('organic'), list) else []
