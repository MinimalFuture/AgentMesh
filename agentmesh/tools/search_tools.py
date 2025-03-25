import json
from typing import Dict, Any, List, Optional
import requests
from agentmesh.tools.base_tool import BaseTool

class GoogleSearchTool(BaseTool):
    """Tool for performing Google searches."""
    
    def __init__(self):
        super().__init__(
            name="google_search",
            description="Search Google for information. Input should be a JSON object with a 'query' field.",
            parameters={
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            }
        )
        self.api_key = "YOUR_API_KEY"  # Replace with your actual API key
        self.search_engine_id = "YOUR_SEARCH_ENGINE_ID"  # Replace with your actual search engine ID
    
    def execute(self, parameters: Dict[str, Any]) -> str:
        """
        Execute the Google search.
        
        :param parameters: The parameters for the search.
        :return: The search results as a string.
        """
        # Ensure parameters is a dictionary
        if isinstance(parameters, str):
            try:
                parameters = json.loads(parameters)
            except json.JSONDecodeError:
                # If it's not valid JSON, assume it's the query itself
                parameters = {"query": parameters}
        
        query = parameters.get("query", "")
        if not query:
            return "Error: No query provided."
        
        try:
            # Perform the search
            url = f"https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query
            }
            response = requests.get(url, params=params)
            
            # Check if the request was successful
            if response.status_code != 200:
                return f"Error: {response.status_code} - {response.text}"
            
            # Parse the response
            search_results = response.json()
            
            # Extract the relevant information
            items = search_results.get("items", [])
            results = []
            
            for i, item in enumerate(items):
                result = {
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "position": i + 1
                }
                
                # Add optional fields if they exist
                if "pagemap" in item and "cse_thumbnail" in item["pagemap"]:
                    result["thumbnail"] = item["pagemap"]["cse_thumbnail"][0].get("src", "")
                
                if "sitelinks" in item:
                    result["sitelinks"] = [
                        {"title": sitelink.get("title", ""), "link": sitelink.get("link", "")}
                        for sitelink in item["sitelinks"].get("sitelinks", [])
                    ]
                
                if "date" in item:
                    result["date"] = item["date"]
                
                results.append(result)
            
            # Return the results as a formatted string
            return json.dumps(results, ensure_ascii=False, indent=2)
        
        except Exception as e:
            return f"Error performing search: {str(e)}" 