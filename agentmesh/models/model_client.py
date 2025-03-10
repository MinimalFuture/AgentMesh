from agentmesh.models import LLMModel, LLMRequest
from agentmesh.common import config


class ModelClient:
    def get_model(self, model_name: str, model_provider: str = "openai"):
        """
        Factory function to get the model instance based on the model name.

        :param model_name: The name of the model to instantiate.
        :return: An instance of the corresponding model.
        """
        model_config = config().get("models").get(model_provider)
        if not model_config:
            raise Exception("No model config")
        return LLMModel(model=model_name, api_base=model_config.get("api_base"), api_key=model_config.get("api_key"))
    
    def call_llm(self, request: LLMRequest):
        """
        Call the model using the provided request parameters.

        :param request: An instance of BaseRequest containing parameters for the model call.
        :return: The response from the model.
        """
        model_instance: LLMModel = self.get_model(request.model)
        return model_instance.call(request)
