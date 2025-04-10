from abc import ABC, abstractmethod
import requests
import json
from typing import Optional


class LLMRequest:
    """
    Represents a request to a model, encapsulating all necessary parameters 
    for making a call to the model.
    """
    def __init__(self, model: str, messages: list,
                 model_provider: Optional[str] = None,
                 temperature=0.5, max_tokens=8192, json_format=False, stream=False):
        """
        Initialize the BaseRequest with the necessary fields.

        :param model: The name of the model to be used.
        :param messages: A list of messages to be sent to the model.
        :param model_provider: Optional. The provider of the model (e.g., 'openai').
                              If not provided, it will be auto-determined.
        :param temperature: The sampling temperature for the model.
        :param max_tokens: The maximum number of tokens to generate.
        :param json_format: Whether to request JSON formatted response.
        :param stream: Whether to enable streaming for the response.
        """
        self.model_provider = model_provider
        self.model = model
        self.messages = messages
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.json_format = json_format
        self.stream = stream


class LLMModel:
    """
    Base class for all AI models. This class provides a common interface for AI model 
    instantiation and calling the model with requests. Subclasses should implement 
    the specific model logic.
    """
    def __init__(self, model: str, api_base: str, api_key: str):
        self.model = model
        self.api_base = api_base
        self.api_key = api_key

    @abstractmethod
    def call(self, request: LLMRequest):
        """
        Call the OpenAI API with the given request parameters.

        :param request: An instance of ModelRequest containing parameters for the API call.
        :return: The response from the OpenAI API.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": request.model,
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }
        if request.json_format:
            data["response_format"] = {"type": "json_object"}

        try:
            response = requests.post(f"{self.api_base}/chat/completions", headers=headers, json=data)
            return response.json()
        except Exception as e:
            print(e)

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
            "model": request.model,
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
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
        except Exception as e:
            print(f"Streaming error: {e}")
