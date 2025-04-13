from enum import Enum


class ModelProvider(Enum):
    """
    Enum representing different model providers.
    """
    OPENAI = "openai"
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    UNKNOWN = "unknown"

    @classmethod
    def from_model_name(cls, model_name: str) -> "ModelProvider":
        """
        Determine the provider based on model name prefix.
        
        :param model_name: The name of the model
        :return: The corresponding ModelProvider enum
        """
        if model_name.startswith(("gpt", "text-davinci", "o1")):
            return cls.OPENAI
        elif model_name.startswith("claude"):
            return cls.CLAUDE
        elif model_name.startswith("deepseek"):
            return cls.DEEPSEEK
        elif model_name.startswith(("qwen", "qwq")):
            return cls.QWEN
        else:
            # Default to OpenAI if no match
            return cls.UNKNOWN


class ModelApiBase(Enum):
    """
    Enum representing default API base URLs for different model providers.
    """
    OPENAI = "https://api.openai.com/v1"
    CLAUDE = "https://api.anthropic.com/v1"
    DEEPSEEK = "https://api.deepseek.com/v1"
    QWEN = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    @classmethod
    def get_api_base(cls, provider: ModelProvider) -> str:
        """
        Get the default API base URL for a provider.
        
        :param provider: The model provider
        :return: The default API base URL
        """
        if not provider:
            return ""
        try:
            return cls[provider.name].value
        except (KeyError, AttributeError):
            return ""
