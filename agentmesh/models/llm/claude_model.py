from agentmesh.models.llm.base_model import LLMModel, LLMRequest
from agentmesh.common.enums import ModelApiBase
import requests
import json


class ClaudeModel(LLMModel):
    def __init__(self, model: str, api_key: str, api_base: str):
        api_base = api_base or ModelApiBase.CLAUDE.value
        super().__init__(model, api_key=api_key, api_base=api_base)

    def call(self, request: LLMRequest):
        """
        Call the Claude API with the given request parameters.

        :param request: An instance of LLMRequest containing parameters for the API call.
        :return: The response from the Claude API, reformatted to match OpenAI's format.
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        # Extract system prompt if present and prepare Claude-compatible messages
        system_prompt = None
        claude_messages = []

        for msg in request.messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                claude_messages.append(msg)

        # Prepare the request data using messages format
        data = {
            "model": self.model,
            "messages": claude_messages,
            "max_tokens": self._get_max_tokens(),
            "temperature": request.temperature
        }

        # Add system parameter if system prompt is present
        if system_prompt:
            data["system"] = system_prompt

        # Add response format if JSON is requested

        try:
            response = requests.post(
                f"{self.api_base}/messages",
                headers=headers,
                json=data
            )

            # Convert Claude response to OpenAI format
            claude_response = response.json()

            # Format the response to match OpenAI's structure
            openai_format_response = {
                "id": claude_response.get("id", ""),
                "object": "chat.completion",
                "created": int(claude_response.get("created_at", 0)),
                "model": self.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": claude_response.get("content", [{}])[0].get("text", "")
                        },
                        "finish_reason": claude_response.get("stop_reason", "stop")
                    }
                ],
                "usage": {
                    "prompt_tokens": claude_response.get("usage", {}).get("input_tokens", 0),
                    "completion_tokens": claude_response.get("usage", {}).get("output_tokens", 0),
                    "total_tokens": claude_response.get("usage", {}).get("input_tokens", 0) +
                                    claude_response.get("usage", {}).get("output_tokens", 0)
                }
            }

            return openai_format_response

        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return {"error": str(e)}

    def call_stream(self, request: LLMRequest):
        """
        Call the Claude API with streaming enabled.

        :param request: An instance of LLMRequest containing parameters for the API call.
        :return: A generator yielding chunks of the response from the Claude API.
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        # Extract system prompt if present and prepare Claude-compatible messages
        system_prompt = None
        claude_messages = []

        for msg in request.messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                claude_messages.append(msg)

        # Prepare the request data using messages format
        data = {
            "model": self.model,
            "messages": claude_messages,
            "max_tokens": self._get_max_tokens(),
            "temperature": request.temperature,
            "stream": True
        }

        # Add system parameter if system prompt is present
        if system_prompt:
            data["system"] = system_prompt

        # Add response format if JSON is requested
        if request.json_format:
            data["response_format"] = {"type": "json_object"}

        try:
            response = requests.post(
                f"{self.api_base}/messages",
                headers=headers,
                json=data,
                stream=True
            )

            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        line = line[6:]  # Remove 'data: ' prefix
                        if line == '[DONE]':
                            break
                        try:
                            chunk = json.loads(line)
                            # Extract content from the delta
                            content = ""
                            if "delta" in chunk and "text" in chunk["delta"]:
                                content = chunk["delta"]["text"]

                            # Convert Claude streaming format to OpenAI format
                            yield {
                                "id": chunk.get("id", ""),
                                "object": "chat.completion.chunk",
                                "created": int(chunk.get("created_at", 0)),
                                "model": self.model,
                                "choices": [
                                    {
                                        "index": 0,
                                        "delta": {
                                            "content": content
                                        },
                                        "finish_reason": None
                                    }
                                ]
                            }
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"Streaming error with Claude API: {e}")

    def _get_max_tokens(self) -> int:
        model = self.model
        if model and (model.startswith("claude-3-5") or model.startswith("claude-3-7")):
            return 8192
        return 4096
