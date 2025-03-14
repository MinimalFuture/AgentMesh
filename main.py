from agentmesh.common import load_config
from agentmesh.tools.tool_manager import ToolManager
from agentmesh.entities import AgentTeam, Agent


if __name__ == "__main__":
    load_config()
    ToolManager().load_tools()