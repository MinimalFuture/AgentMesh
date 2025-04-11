from agentmesh.models.llm.base_model import LLMModel


class OpenAIModel(LLMModel):
    def __init__(self, model: str, api_key: str,  api_base: str):
        super().__init__(model, api_key=api_key, api_base=api_base)
        self.api_base = api_base or "https://api.openai.com/v1"
