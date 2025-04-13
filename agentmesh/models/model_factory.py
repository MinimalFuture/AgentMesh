from typing import Optional

from agentmesh.common import config
from agentmesh.models.llm.base_model import LLMModel
from agentmesh.models.llm.claude_model import ClaudeModel
from agentmesh.models.llm.deepseek_model import DeepSeekModel
from agentmesh.models.llm.openai_model import OpenAIModel


class ModelFactory:
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

    def get_model(self, model_name: str, model_provider: Optional[str] = None,
                  api_base: Optional[str] = None, api_key: Optional[str] = None) -> LLMModel:
        """
        Factory function to get the model instance based on the model name.

        :param model_name: The name of the model to instantiate.
        :param model_provider: Optional provider of the model (will be auto-determined if not provided).
        :param api_base: Optional API base URL. If not provided, will be loaded from config.
        :param api_key: Optional API key. If not provided, will be loaded from config.
        :return: An instance of the corresponding model.
        """
        provider = self._determine_model_provider(model_name, model_provider)

        # If api_base and api_key are not provided, load from config
        if not api_base or not api_key:
            model_config = config().get("models", {}).get(provider, {})
            api_base = api_base or model_config.get("api_base")
            api_key = api_key or model_config.get("api_key")

        if provider == "openai":
            return OpenAIModel(model=model_name, api_base=api_base, api_key=api_key)
        elif provider == "claude":
            return ClaudeModel(model=model_name, api_base=api_base, api_key=api_key)
        elif provider == "deepseek":
            return DeepSeekModel(model=model_name, api_base=api_base, api_key=api_key)
        else:
            # Default to base LLMModel if provider is not recognized
            return LLMModel(model=model_name, api_base=api_base, api_key=api_key)
