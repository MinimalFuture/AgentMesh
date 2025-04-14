from agentmesh.models.llm.base_model import LLMModel, LLMRequest, LLMResponse
from agentmesh.common.enums import ModelApiBase
import requests
import json


class ClaudeModel(LLMModel):
    def __init__(self, model: str, api_key: str, api_base: str = None):
        api_base = api_base or ModelApiBase.CLAUDE.value
        super().__init__(model, api_key=api_key, api_base=api_base)

    def call(self, request: LLMRequest) -> LLMResponse:
        """
        Call the Claude API with the given request parameters.

        :param request: An instance of LLMRequest containing parameters for the API call.
        :return: An LLMResponse object containing the response or error information.
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

        try:
            response = requests.post(
                f"{self.api_base}/messages",
                headers=headers,
                json=data
            )

            # Check if the request was successful
            if response.status_code == 200:
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

                return LLMResponse(success=True, data=openai_format_response, status_code=response.status_code)
            else:
                # Try to extract error message from response
                error_msg = "Unknown error"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        if isinstance(error_data["error"], dict) and "message" in error_data["error"]:
                            error_msg = error_data["error"]["message"]
                        else:
                            error_msg = str(error_data["error"])
                    elif "message" in error_data:
                        error_msg = error_data["message"]
                    else:
                        error_msg = response.text
                except:
                    error_msg = response.text or "Could not parse error response"

                return LLMResponse(
                    success=False,
                    error_message=error_msg,
                    status_code=response.status_code
                )

        except requests.RequestException as e:
            # Handle connection errors, timeouts, etc.
            return LLMResponse(
                success=False,
                error_message=f"Request failed: {str(e)}",
                status_code=0  # Use 0 for connection errors
            )
        except Exception as e:
            # Handle any other exceptions
            return LLMResponse(
                success=False,
                error_message=f"Unexpected error: {str(e)}",
                status_code=500
            )

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

            # Check for error response
            if response.status_code != 200:
                # Try to extract error message
                try:
                    error_data = json.loads(response.text)
                    if "error" in error_data:
                        if isinstance(error_data["error"], dict) and "message" in error_data["error"]:
                            error_msg = error_data["error"]["message"]
                        else:
                            error_msg = str(error_data["error"])
                    elif "message" in error_data:
                        error_msg = error_data["message"]
                    else:
                        error_msg = response.text
                except:
                    error_msg = response.text or "Unknown error"

                # Yield an error object that can be detected by the caller
                yield {
                    "error": True,
                    "status_code": response.status_code,
                    "message": error_msg
                }
                return

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
        except requests.RequestException as e:
            # Yield an error object for connection errors
            yield {
                "error": True,
                "status_code": 0,
                "message": f"Connection error: {str(e)}"
            }
        except Exception as e:
            # Yield an error object for unexpected errors
            yield {
                "error": True,
                "status_code": 500,
                "message": f"Unexpected error: {str(e)}"
            }

    def _get_max_tokens(self) -> int:
        model = self.model
        if model and (model.startswith("claude-3-5") or model.startswith("claude-3-7")):
            return 8192
        return 4096
