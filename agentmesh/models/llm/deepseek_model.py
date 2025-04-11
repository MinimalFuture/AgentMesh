from agentmesh.models.llm.base_model import LLMModel


class DeepSeekModel(LLMModel):
    def __init__(self, model: str, api_key: str, api_base: str):
        super().__init__(model, api_key=api_key, api_base=api_base)
        self.api_base = api_base or "https://api.deepseek.com/v1"
