import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

from agentmesh.protocal.task import Task, TaskStatus


class AgentActionType(Enum):
    """Enum representing different types of agent actions."""
    TOOL_USE = "tool_use"
    THINKING = "thinking"
    FINAL_ANSWER = "final_answer"


@dataclass
class ToolResult:
    """
    Represents the result of a tool use.
    
    Attributes:
        tool_name: Name of the tool used
        input_params: Parameters passed to the tool
        output: Output from the tool
        status: Status of the tool execution (success/error)
        error_message: Error message if the tool execution failed
        execution_time: Time taken to execute the tool
    """
    tool_name: str
    input_params: Dict[str, Any]
    output: Any
    status: str
    error_message: Optional[str] = None
    execution_time: float = 0.0


@dataclass
class AgentAction:
    """
    Represents an action taken by an agent.
    
    Attributes:
        id: Unique identifier for the action
        agent_id: ID of the agent that performed the action
        agent_name: Name of the agent that performed the action
        action_type: Type of action (tool use, thinking, final answer)
        content: Content of the action (thought content, final answer content)
        tool_result: Tool use details if action_type is TOOL_USE
        timestamp: When the action was performed
    """
    agent_id: str
    agent_name: str
    action_type: AgentActionType
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    tool_result: Optional[ToolResult] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class AgentExecutionResult:
    """
    Represents the execution result of a single agent.
    
    Attributes:
        agent_id: ID of the agent
        agent_name: Name of the agent
        subtask: The subtask assigned to the agent
        actions: List of actions performed by the agent
        final_answer: The final answer provided by the agent
        start_time: When the agent started execution
        end_time: When the agent finished execution
        execution_time: Total time taken by the agent
    """
    agent_id: str
    agent_name: str
    subtask: str
    actions: List[AgentAction] = field(default_factory=list)
    final_answer: str = ""
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0

    @property
    def execution_time(self) -> float:
        """Calculate the total execution time."""
        if self.end_time > 0:
            return self.end_time - self.start_time
        return 0.0

    def add_action(self, action: AgentAction) -> None:
        """Add an action to the agent's execution history."""
        self.actions.append(action)

        # If this is a final answer, update the final_answer field
        if action.action_type == AgentActionType.FINAL_ANSWER:
            self.final_answer = action.content

    def complete(self) -> None:
        """Mark the agent execution as complete."""
        self.end_time = time.time()


@dataclass
class TeamResult:
    """
    Represents the result of a team run.
    
    Attributes:
        id: Unique identifier for the run
        team_name: Name of the team
        task: The task that was processed
        agent_results: Results from each agent that was executed
        final_output: The final output of the team run
        start_time: When the team run started
        end_time: When the team run finished
        status: Status of the team run
    """
    team_name: str
    task: Task
    id: str = field(default=None)
    agent_results: List[AgentExecutionResult] = field(default_factory=list)
    final_output: str = ""
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0
    status: str = "running"

    def __post_init__(self):
        """Initialize id with task id if not provided"""
        if self.id is None and self.task:
            self.id = self.task.id

    @property
    def execution_time(self) -> float:
        """Calculate the total execution time."""
        if self.end_time > 0:
            return self.end_time - self.start_time
        return 0.0

    def add_agent_result(self, agent_result: AgentExecutionResult) -> None:
        """Add an agent result to the team run."""
        self.agent_results.append(agent_result)

        # 更新最终输出为最新代理的最终答案（如果有）
        if agent_result.final_answer:
            self.final_output = agent_result.final_answer

    def complete(self, status: str = "completed") -> None:
        """Mark the team run as complete."""
        self.end_time = time.time()
        self.status = status

        # Update task status
        if self.task:
            if status == "completed":
                self.task.update_status(TaskStatus.COMPLETED)
            elif status == "failed":
                self.task.update_status(TaskStatus.FAILED)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary for serialization."""
        return {
            "id": self.id,
            "team_name": self.team_name,
            "task": {
                "id": self.task.id,
                "content": self.task.get_text(),
                "type": self.task.type.value,
                "status": self.task.status.value
            },
            "agent_results": [
                {
                    "agent_id": ar.agent_id,
                    "agent_name": ar.agent_name,
                    "subtask": ar.subtask,
                    "final_answer": ar.final_answer,
                    "execution_time": ar.execution_time,
                    "actions": [
                        {
                            "id": action.id,
                            "agent_name": action.agent_name,
                            "action_type": action.action_type.value,
                            "content": action.content,
                            "tool_result": {
                                "tool_name": action.tool_result.tool_name,
                                "input_params": action.tool_result.input_params,
                                "output": action.tool_result.output,
                                "status": action.tool_result.status,
                                "execution_time": action.tool_result.execution_time
                            } if action.tool_result else None,
                            "timestamp": action.timestamp
                        }
                        for action in ar.actions
                    ]
                }
                for ar in self.agent_results
            ],
            "final_output": self.final_output,
            "execution_time": self.execution_time,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status
        }
