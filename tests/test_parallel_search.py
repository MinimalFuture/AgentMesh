"""Exercise native loading, agent dispatch and the prepared HTTP MCP requests."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import requests
import yaml

from agentmesh import Agent
from agentmesh.tools import ParallelSearch, ToolManager


ARGS = {"objective": "Find Python asyncio documentation",
        "search_queries": ["Python asyncio tasks documentation"]}
SEARCH_RESULT = {"content": [{"type": "text", "text": "Python asyncio tasks: café"}],
                 "structuredContent": {"results": [{"url": "https://docs.python.org/3/library/asyncio-task.html",
                                                   "excerpts": ["Tasks schedule coroutines concurrently."]}]}}


class MCPTransport:
    """Intercept send, after requests has prepared URL, headers and JSON body."""
    def __init__(self, sse=False, error=None):
        self.sse = sse
        self.error = error
        self.requests = []

    def send(self, request, **kwargs):
        self.requests.append((request, kwargs))
        response = requests.Response()
        response.request = request
        response.url = request.url
        response.status_code = 200
        response.encoding = "utf-8"
        response.headers["Content-Type"] = "application/json"
        payload = json.loads(request.body) if request.body else {}
        method = payload.get("method")
        if method == "initialize":
            result = {"protocolVersion": ParallelSearch.PROTOCOL_VERSION}
            response.headers["Mcp-Session-Id"] = "transport-session"
        elif method == "tools/call":
            if self.error == "timeout":
                raise requests.Timeout("read timed out")
            if self.error == "429":
                response.status_code = 429
                response.headers["Retry-After"] = "120"
            result = dict(SEARCH_RESULT)
            if self.error == "tool":
                result = {"isError": True, "content": [{"type": "text", "text": "Search failed"}]}
        else:
            result = {}
        message = {"jsonrpc": "2.0", "id": payload.get("id"), "result": result}
        if method == "tools/call" and self.error == "rpc":
            message = {"jsonrpc": "2.0", "id": payload["id"], "error": {"code": -32603, "message": "Unavailable"}}
        if method == "tools/call" and self.error == "id":
            message["id"] = 999
        if method == "tools/call" and self.error == "malformed":
            message = []
        if self.sse and method in ("initialize", "tools/call"):
            response.headers["Content-Type"] = "text/event-stream"
            # A comment, a notification, then multiline UTF-8 result data.
            notification = 'data: {"jsonrpc":"2.0","method":"notifications/message"}\n\n'
            event = "\n".join("data: " + line for line in json.dumps(message, ensure_ascii=False, indent=2).splitlines())
            response._content = (": keepalive\n\n" + notification + event + "\n\n").encode("utf-8")
        else:
            response._content = json.dumps(message).encode()
        response._content_consumed = True
        return response


class ParallelSearchTests(unittest.TestCase):
    def setUp(self):
        ToolManager._instance = None

    def test_loading_and_defaults(self):
        manager = ToolManager()
        manager.load_tools(config_dict={"parallel_search": {"timeout": 12}})
        self.assertIsInstance(manager.create_tool("parallel_search"), ParallelSearch)
        self.assertEqual(manager.create_tool("parallel_search").config, {"timeout": 12})
        self.assertEqual(manager.create_tool("google_search").name, "google_search")
        template = yaml.safe_load(Path("config-template.yaml").read_text())
        self.assertIn("google_search", template["teams"]["general_team"]["agents"][0]["tools"])
        for team in template["teams"].values():
            for agent in team["agents"]:
                self.assertNotIn("parallel_search", agent.get("tools", []))

    def test_anonymous_json_and_sse(self):
        for sse in (False, True):
            with self.subTest(sse=sse), tempfile.TemporaryDirectory() as home:
                # Saved HTTP credentials must not silently authenticate the free path.
                netrc = Path(home) / ".netrc"
                netrc.write_text("machine search.parallel.ai login saved password secret\n")
                transport = MCPTransport(sse=sse)
                tool = ParallelSearch({"timeout": 12})
                with patch.dict(os.environ, {"NETRC": str(netrc), "PARALLEL_API_KEY": "unused"}), patch.object(requests.Session, "send", transport.send):
                    for _ in range(2):
                        result = tool.execute(ARGS)
                        self.assertEqual(result.status, "success")
                        self.assertEqual(result.result, SEARCH_RESULT)
                for request, options in transport.requests:
                    self.assertEqual(request.url, ParallelSearch.URL)
                    self.assertEqual(request.headers["User-Agent"], ParallelSearch.USER_AGENT)
                    self.assertNotIn("Authorization", request.headers)
                    self.assertEqual(options["timeout"], 5 if request.method == "DELETE" else 12)
                    if request.body:
                        payload = json.loads(request.body)
                        if payload["method"] != "initialize":
                            self.assertEqual(request.headers["Mcp-Session-Id"], "transport-session")
                            self.assertEqual(request.headers["MCP-Protocol-Version"], ParallelSearch.PROTOCOL_VERSION)
                        if payload["method"] == "tools/call":
                            self.assertEqual(payload["params"]["name"], "web_search")
                            self.assertEqual(payload["params"]["arguments"], dict(ARGS, session_id=tool.session_id))
                self.assertEqual(len(transport.requests), 8)

    def test_errors_do_not_retry_and_cleanup(self):
        for error in ("429", "timeout", "tool", "rpc", "id", "malformed"):
            with self.subTest(error=error):
                transport = MCPTransport(error=error)
                with patch.object(requests.Session, "send", transport.send):
                    result = ParallelSearch().execute(ARGS)
                self.assertEqual(result.status, "error")
                self.assertEqual(len(transport.requests), 4)
                self.assertEqual(transport.requests[-1][0].method, "DELETE")
                if error == "429":
                    self.assertEqual(result.ext_data, {"http_status": 429, "retry_after": "120"})

    def test_invalid_input_never_connects(self):
        with patch.object(requests.Session, "send") as send:
            for args in ({}, dict(ARGS, objective=""), dict(ARGS, search_queries=[]), dict(ARGS, search_queries=[1])):
                self.assertEqual(ParallelSearch().execute(args).status, "error")
            for timeout in (None, 0, -1, float("inf"), True):
                self.assertEqual(ParallelSearch({"timeout": timeout}).execute(ARGS).status, "error")
            send.assert_not_called()

    def test_agent_loop_dispatches_registered_tool_and_receives_sources(self):
        test = self

        class ScriptedModel:
            model = "fixture-model"
            calls = 0

            def call_stream(self, request):
                self.calls += 1
                test.assertEqual(request.tools[0]["name"], "parallel_search")
                if self.calls == 1:
                    yield {"choices": [{"delta": {"tool_calls": [{"index": 0, "id": "search-1", "function": {
                        "name": "parallel_search", "arguments": json.dumps(ARGS)}}]}}]}
                else:
                    result = json.loads(request.messages[-1]["content"][0]["content"])
                    test.assertEqual(result["status"], "success")
                    test.assertEqual(result["result"], SEARCH_RESULT)
                    yield {"choices": [{"delta": {"content": "Tasks schedule coroutines concurrently."}}]}

        manager = ToolManager()
        manager.load_tools()
        model = ScriptedModel()
        agent = Agent("Researcher", "Search for sources.", "Research", model=model,
                      tools=[manager.create_tool("parallel_search")], max_steps=3)
        transport = MCPTransport(sse=True)
        with patch.object(requests.Session, "send", transport.send):
            self.assertEqual(agent.run_stream("Find asyncio tasks"), "Tasks schedule coroutines concurrently.")
        self.assertEqual(model.calls, 2)
        self.assertEqual(len(transport.requests), 4)


if __name__ == "__main__":
    unittest.main()
