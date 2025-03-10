from abc import ABC, abstractmethod
import requests


class LLMRequest:
    """
    Represents a request to a model, encapsulating all necessary parameters 
    for making a call to the model.
    """
    def __init__(self, model_provider: str, model: str, messages: list,
                 temperature=0.7, max_tokens=150, json_format=False):
        """
        Initialize the BaseRequest with the necessary fields.

        :param model: The name of the model to be used.
        :param messages: A list of messages to be sent to the model.
        :param temperature: The sampling temperature for the model.
        :param max_tokens: The maximum number of tokens to generate.
        """
        self.model_provider = model_provider
        self.model = model
        self.messages = messages
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.json_format = json_format


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
