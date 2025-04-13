# First, set environment variables before any imports
import os

os.environ["BROWSER_USE_LOGGING_LEVEL"] = "error"

# Then import logging and configure it
import logging

logging.getLogger("browser_use").setLevel(logging.ERROR)
logging.getLogger("root").setLevel(logging.ERROR)

# Now import the rest
from agentmesh.protocal import Agent, AgentTeam
from agentmesh.protocal.task import Task
from agentmesh.protocal.result import TeamResult
from agentmesh.models import LLMModel
from agentmesh.common.utils.log import setup_logging

# Setup logging when the package is imported
setup_logging()

__all__ = ['AgentTeam', 'Agent', 'LLMModel', 'Task', 'TeamResult']
