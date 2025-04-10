from agentmesh.models.llm.base_model import LLMModel


class OpenAIModel(LLMModel):
    def __init__(self, model: str, api_base: str, api_key: str):
        super().__init__(model, api_base, api_key)
        self.api_base = api_base or "https://api.openai.com/v1"
