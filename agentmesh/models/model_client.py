from agentmesh.models import LLMModel, LLMRequest
from agentmesh.common import config
from typing import Iterator, Optional


class ModelClient:
    def _get_model_instance(self, model_provider: str, model_name: str) -> LLMModel:
        """
        Get a model instance based on the provider and model name.

        :param model_provider: The provider of the model (e.g., "openai").
        :param model_name: The name of the model to instantiate.
        :return: An instance of the corresponding model.
        """
        model_config = config().get("models", {}).get(model_provider)
        if not model_config:
            raise Exception(f"No model config found for provider: {model_provider}")
        return LLMModel(model=model_name, api_base=model_config.get("api_base"), api_key=model_config.get("api_key"))

    def _determine_model_provider(self, model_name: str, model_provider: Optional[str] = None) -> str:
        """
        Determine the appropriate model provider based on model name and configuration.
        
        :param model_name: The name of the model.
        :param model_provider: Optional explicitly specified provider.
        :return: The determined model provider.
        """
        # If provider is explicitly specified, use it
        if model_provider:
            return model_provider
            
        # Get models configuration
        models_config = config().get("models", {})
        
        # Strategy 1: Check if model is listed in any provider's models list
        for provider, provider_config in models_config.items():
            provider_models = provider_config.get("models", [])
            if model_name in provider_models:
                return provider
        
        # Strategy 2: Determine provider based on model name prefix
        if model_name.startswith(("gpt", "text-davinci", "o1")):
            return "openai"
        elif model_name.startswith("claude"):
            return "claude"
        elif model_name.startswith("deepseek"):
            return "deepseek"
        
        # Strategy 3: Default to openai if no match
        return "openai"

    def get_model(self, model_name: str, model_provider: Optional[str] = None) -> LLMModel:
        """
        Factory function to get the model instance based on the model name.

        :param model_name: The name of the model to instantiate.
        :param model_provider: Optional provider of the model (will be auto-determined if not provided).
        :return: An instance of the corresponding model.
        """
        provider = self._determine_model_provider(model_name, model_provider)
        return self._get_model_instance(provider, model_name)

    def llm(self, request: LLMRequest):
        """
        Call the model using the provided request parameters.

        :param request: An instance of LLMRequest containing parameters for the model call.
        :return: The response from the model.
        """
        # Auto-determine provider if not specified
        if not request.model_provider:
            request.model_provider = self._determine_model_provider(request.model)
            
        model_instance = self.get_model(request.model, request.model_provider)
        return model_instance.call(request)

    def llm_stream(self, request: LLMRequest) -> Iterator[dict]:
        """
        Stream a response from the LLM.

        :param request: The request to send to the LLM.
        :return: An iterator of response chunks.
        """
        # Auto-determine provider if not specified
        if not request.model_provider:
            request.model_provider = self._determine_model_provider(request.model)
            
        model_provider = request.model_provider
        model = request.model

        # Get the model instance
        model_instance = self.get_model(model, model_provider)

        # Stream the response
        return model_instance.call_stream(request)
