from agentmesh.models.llm.base_model import LLMModel
from agentmesh.common.enums import ModelApiBase


class OpenAIModel(LLMModel):
    def __init__(self, model: str, api_key: str, api_base: str):
        api_base = api_base or ModelApiBase.OPENAI.value
        super().__init__(model, api_key=api_key, api_base=api_base)
