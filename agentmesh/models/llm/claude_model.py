from agentmesh.models.llm.base_model import LLMModel, LLMRequest


class ClaudeModel(LLMModel):
    def __init__(self, model: str, api_base: str, api_key: str):
        super().__init__(model, api_base, api_key)

    def call(self, request: LLMRequest):
        pass
