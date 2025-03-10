class GroupContext:
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
        self.user_question = ""
        # List of agents that have been executed
        self.executed_agents = []
