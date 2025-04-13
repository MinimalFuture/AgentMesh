from abc import abstractmethod
import requests
import json
from agentmesh.common.enums import ModelApiBase, ModelProvider
from typing import Optional, Dict, Any


class LLMRequest:
    """
    Represents a request to a model, encapsulating all necessary parameters 
    for making a call to the model.
    """

    def __init__(self, messages: list,
                 temperature=0.5, json_format=False, stream=False):
        """
        Initialize the BaseRequest with the necessary fields.

        :param messages: A list of messages to be sent to the model.
        :param temperature: The sampling temperature for the model.
        :param json_format: Whether to request JSON formatted response.
        :param stream: Whether to enable streaming for the response.
        """
        self.messages = messages
        self.temperature = temperature
        self.json_format = json_format
        self.stream = stream


class LLMResponse:
    """
    Represents a response from an LLM API call, including error handling.
    """

    def __init__(self, success: bool = True, data: Optional[Dict[str, Any]] = None,
                 error_message: str = "", status_code: int = 200):
        self.success = success
        self.data = data or {}
        self.error_message = error_message
        self.status_code = status_code

    @property
    def is_error(self) -> bool:
        return not self.success

    def get_error_msg(self) -> str:
        """Return a user-friendly error message based on status code and error details"""
        if not self.is_error:
            return ""

        # If there is a specific error message, prioritize using the API's error message
        if self.error_message and self.error_message != "Unknown error":
            return f"API error: {self.error_message} (Status code: {self.status_code})"

        # If there is no specific error message, provide a generic error message based on status code
        if self.status_code == 401:
            return f"Authentication error: Invalid API key or token. Please check your API credentials. (Status code: {self.status_code})"
        elif self.status_code == 403:
            return f"Authorization error: You don't have permission to access this resource. (Status code: {self.status_code})"
        elif self.status_code == 404:
            return f"Resource not found: The requested endpoint doesn't exist. Please check your API base URL. (Status code: {self.status_code})"
        elif self.status_code == 429:
            return f"Rate limit exceeded: Too many requests. Please try again later or check your rate limits. (Status code: {self.status_code})"
        elif self.status_code >= 500:
            return f"Server error: The API service is experiencing issues. Please try again later. (Status code: {self.status_code})"
        else:
            # Default error message
            return f"API error: Unknown error occurred (Status code: {self.status_code})"


class LLMModel:
    """
    Base class for all AI models. This class provides a common interface for AI model 
    instantiation and calling the model with requests. Subclasses should implement 
    the specific model logic.
    """

    def __init__(self, model: str, api_key: str, api_base: str = None):
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        if not api_base:
            provider = ModelProvider.from_model_name(model)
            self.api_base = ModelApiBase.get_api_base(provider)

    @abstractmethod
    def call(self, request: LLMRequest) -> LLMResponse:
        """
        Call the API with the given request parameters.

        :param request: An instance of ModelRequest containing parameters for the API call.
        :return: An LLMResponse object containing the response or error information.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": request.messages,
            "temperature": request.temperature,
        }
        if request.json_format:
            data["response_format"] = {"type": "json_object"}

        try:
            response = requests.post(f"{self.api_base}/chat/completions", headers=headers, json=data)

            # Check if the request was successful
            if response.status_code == 200:
                return LLMResponse(success=True, data=response.json(), status_code=response.status_code)
            else:
                # Try to extract error message from response
                error_msg = "Unknown error"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        if isinstance(error_data["error"], dict) and "message" in error_data["error"]:
                            error_msg = error_data["error"]["message"]
                        else:
                            error_msg = str(error_data["error"])
                    elif "message" in error_data:
                        error_msg = error_data["message"]
                except:
                    error_msg = response.text or "Could not parse error response"

                return LLMResponse(
                    success=False,
                    error_message=error_msg,
                    status_code=response.status_code
                )

        except requests.RequestException as e:
            # Handle connection errors, timeouts, etc.
            return LLMResponse(
                success=False,
                error_message=f"Request failed: {str(e)}",
                status_code=0  # Use 0 for connection errors
            )
        except Exception as e:
            # Handle any other exceptions
            return LLMResponse(
                success=False,
                error_message=f"Unexpected error: {str(e)}",
                status_code=500
            )

    def call_stream(self, request: LLMRequest):
        """
        Call the OpenAI API with streaming enabled.

        :param request: An instance of LLMRequest containing parameters for the API call.
        :return: A generator yielding chunks of the response from the OpenAI API.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": request.messages,
            "temperature": request.temperature,
            "stream": True  # Enable streaming
        }
        if request.json_format:
            data["response_format"] = {"type": "json_object"}

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                stream=True
            )

            # Check for error response
            if response.status_code != 200:
                # Try to extract error message
                try:
                    error_data = json.loads(response.text)
                    if "error" in error_data:
                        if isinstance(error_data["error"], dict) and "message" in error_data["error"]:
                            error_msg = error_data["error"]["message"]
                        else:
                            error_msg = str(error_data["error"])
                    elif "message" in error_data:
                        error_msg = error_data["message"]
                    else:
                        error_msg = response.text
                except:
                    error_msg = response.text or "Unknown error"

                # Yield an error object that can be detected by the caller
                yield {
                    "error": True,
                    "status_code": response.status_code,
                    "message": error_msg
                }
                return

            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        line = line[6:]  # Remove 'data: ' prefix
                        if line == '[DONE]':
                            break
                        try:
                            chunk = json.loads(line)
                            yield chunk
                        except json.JSONDecodeError:
                            continue
        except requests.RequestException as e:
            # Yield an error object for connection errors
            yield {
                "error": True,
                "status_code": 0,
                "message": f"Connection error: {str(e)}"
            }
        except Exception as e:
            # Yield an error object for unexpected errors
            yield {
                "error": True,
                "status_code": 500,
                "message": f"Unexpected error: {str(e)}"
            }
