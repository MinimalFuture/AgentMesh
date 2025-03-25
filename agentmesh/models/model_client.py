from agentmesh.models import LLMModel, LLMRequest
from agentmesh.common import config
from typing import Iterator


class ModelClient:
    def _get_model_instance(self, model_provider: str, model_name: str) -> LLMModel:
        """
        Get a model instance based on the provider and model name.

        :param model_provider: The provider of the model (e.g., "openai").
        :param model_name: The name of the model to instantiate.
        :return: An instance of the corresponding model.
        """
        model_config = config().get("models").get(model_provider)
        if not model_config:
            raise Exception(f"No model config found for provider: {model_provider}")
        return LLMModel(model=model_name, api_base=model_config.get("api_base"), api_key=model_config.get("api_key"))

    def get_model(self, model_name: str, model_provider: str = "openai") -> LLMModel:
        """
        Factory function to get the model instance based on the model name.

        :param model_name: The name of the model to instantiate.
        :param model_provider: The provider of the model (default: "openai").
        :return: An instance of the corresponding model.
        """
        return self._get_model_instance(model_provider, model_name)

    def llm(self, request: LLMRequest):
        """
        Call the model using the provided request parameters.

        :param request: An instance of LLMRequest containing parameters for the model call.
        :return: The response from the model.
        """
        model_instance = self.get_model(request.model, request.model_provider)
        return model_instance.call(request)

    def llm_stream(self, request: LLMRequest) -> Iterator[dict]:
        """
        Stream a response from the LLM.

        :param request: The request to send to the LLM.
        :return: An iterator of response chunks.
        """
        model_provider = request.model_provider
        model = request.model

        # Get the model instance
        model_instance = self.get_model(model, model_provider)

        # Stream the response
        return model_instance.call_stream(request)
