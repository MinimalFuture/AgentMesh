class TeamContext:
    def __init__(self, name: str, description: str, rule: str, agents: list):
        """
        Initialize the GroupContext with a name, description, rules, a list of agents, and a user question.
        :param name: The name of the group context.
        :param description: A description of the group context.
        :param rule: The rules governing the group context.
        :param agents: A list of agents in the context.
        """
        self.name = name
        self.description = description
        self.rule = rule
        self.agents = agents
        self.user_task = ""  # For backward compatibility
        self.task = None  # Will be a Task instance
        self.model = None  # Will be an instance of LLMModel
        # List of agents that have been executed
        self.agent_outputs: list = []


class AgentOutput:
    def __init__(self, agent_name: str, output: str):
        self.agent_name = agent_name
        self.output = output
