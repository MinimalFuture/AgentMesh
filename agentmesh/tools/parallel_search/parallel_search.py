"""Opt-in anonymous web search through Parallel's HTTP MCP server."""
import json
import math
import uuid

import requests

from agentmesh.tools.base_tool import BaseTool, ToolResult


class _AnonymousAuth(requests.auth.AuthBase):
    def __call__(self, request):
        # Prevent requests from adding credentials from ~/.netrc.
        return request


class ParallelSearch(BaseTool):
    name = "parallel_search"
    description = (
        "Search the web for current information using Parallel Search MCP. "
        "Returns source URLs and relevant excerpts, without a Parallel API key."
    )
    params = {
        "type": "object",
        "properties": {
            "objective": {
                "type": "string",
                "description": "The specific information to find, including freshness or source preferences."
            },
            "search_queries": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "description": "Related keyword queries of 3-6 words each; use 2-3 for best results."
            }
        },
        "required": ["objective", "search_queries"]
    }
    URL = "https://search.parallel.ai/mcp"
    USER_AGENT = "AgentMesh/ParallelSearchMCP"
    PROTOCOL_VERSION = "2025-03-26"

    def __init__(self, config=None):
        self.config = config or {}
        # Reuse this value across calls made by this agent's tool instance.
        self.session_id = str(uuid.uuid4())

    def _rpc(self, session, method, params, request_id=None):
        payload = {"jsonrpc": "2.0", "method": method, "params": params}
        if request_id is not None:
            payload["id"] = request_id
        with session.post(
            self.URL, json=payload, timeout=self.config.get("timeout", 60), stream=True
        ) as response:
            response.raise_for_status()
            if method == "initialize" and response.headers.get("Mcp-Session-Id"):
                session.headers["Mcp-Session-Id"] = response.headers["Mcp-Session-Id"]
            if request_id is None:
                return None
            if response.headers.get("Content-Type", "").startswith("text/event-stream"):
                response.encoding = "utf-8"
                # Read complete SSE events, allowing comments, notifications and multiline data.
                data = []
                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        if data:
                            message = json.loads("\n".join(data))
                            data = []
                            if isinstance(message, dict) and message.get("id") == request_id:
                                break
                    elif line.startswith("data:"):
                        data.append(line[5:].lstrip(" "))
                else:
                    raise ValueError("MCP stream ended without a matching response")
            else:
                message = response.json()
            if not isinstance(message, dict) or message.get("id") != request_id:
                raise ValueError("MCP response ID does not match the request")
            if "error" in message:
                raise ValueError("MCP error: " + str(message["error"]))
            if not isinstance(message.get("result"), dict):
                raise ValueError("MCP response is missing a result object")
            return message["result"]

    def execute(self, args: dict) -> ToolResult:
        timeout = self.config.get("timeout", 60)
        if (not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or
                not math.isfinite(timeout) or timeout <= 0):
            return ToolResult.fail("timeout must be a positive finite number of seconds")
        objective = args.get("objective")
        queries = args.get("search_queries")
        if not isinstance(objective, str) or not objective.strip():
            return ToolResult.fail("objective must be a nonempty string")
        if (not isinstance(queries, list) or not queries or
                any(not isinstance(q, str) or not q.strip() for q in queries)):
            return ToolResult.fail("search_queries must contain nonempty strings")

        with requests.Session() as session:
            session.auth = _AnonymousAuth()
            session.headers.update({
                "User-Agent": self.USER_AGENT,
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json"
            })
            try:
                initialized = self._rpc(session, "initialize", {
                    "protocolVersion": self.PROTOCOL_VERSION,
                    "capabilities": {},
                    "clientInfo": {"name": "AgentMesh", "version": "0.1.6"}
                }, 1)
                if initialized.get("protocolVersion") != self.PROTOCOL_VERSION:
                    raise ValueError("Unsupported MCP protocol version")
                session.headers["MCP-Protocol-Version"] = self.PROTOCOL_VERSION
                self._rpc(session, "notifications/initialized", {})
                result = self._rpc(session, "tools/call", {
                    "name": "web_search",
                    "arguments": {
                        "objective": objective,
                        "search_queries": queries,
                        "session_id": self.session_id
                    }
                }, 2)
                # Keep the full MCP result, including structuredContent, citations and warnings.
                if result.get("isError"):
                    return ToolResult.fail(result)
                return ToolResult.success(result)
            except requests.HTTPError as exc:
                return ToolResult.fail(str(exc), ext_data={
                    "http_status": exc.response.status_code,
                    "retry_after": exc.response.headers.get("Retry-After")
                })
            except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
                return ToolResult.fail("Parallel Search MCP: " + str(exc))
            finally:
                if "Mcp-Session-Id" in session.headers:
                    # Session cleanup must not replace the search result or trigger a retry.
                    try:
                        with session.delete(self.URL, timeout=5):
                            pass
                    except requests.RequestException:
                        pass
