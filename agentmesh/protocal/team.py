from agentmesh.common import LoadingIndicator
from agentmesh.common.utils import string_util
from agentmesh.models import LLMRequest
from agentmesh.models.model_client import ModelClient
from agentmesh.protocal.agent import Agent
from agentmesh.protocal.context import TeamContext


class AgentTeam:
    def __init__(self, name: str, description: str, rule: str):
        """
        Initialize the AgentTeam with a name, description, rules, and a list of agents.

        :param name: The name of the agent group.
        :param description: A description of the agent group.
        :param rule: The rules governing the agent group.
        """
        self.name = name
        self.description = description
        self.rule = rule
        self.agents = []
        self.context = TeamContext(name, description, rule, agents=self.agents)

    def add(self, agent: Agent):
        """
        Add an agent to the group.

        :param agent: The agent to be added.
        """
        agent.team_context = self.context  # Pass the group context to the agent
        self.agents.append(agent)

    def run(self, task: str):
        """
        Decide which agent will handle the task and execute its step method.
        """
        self.context.user_task = task
        model_client = ModelClient()

        # Print user task and team information
        print(f"User Task: {task}")
        print(f"Team {self.name} received the task and started processing")
        print()

        # Generate agents_str from the list of agents
        agents_str = ', '.join(
            f'{{"id": {i}, "name": "{agent.name}", "description": "{agent.description}", "system_prompt": "{agent.system_prompt}"}}'
            for i, agent in enumerate(self.agents)
        )

        prompt = GROUP_DECISION_PROMPT.format(group_name=self.name, group_description=self.description,
                                              group_rules=self.rule, agents_str=agents_str, user_question=task)

        # Start loading animation
        loading = LoadingIndicator(message="Select an agent in the team...", animation_type="spinner")
        loading.start()

        request = LLMRequest(model_provider="openai",
                             model="gpt-4o-mini",
                             messages=[{
                                 "role": "user",
                                 "content": prompt
                             }],
                             temperature=0,
                             max_tokens=150,
                             json_format=True)

        # Get the model instance and decide which agent to use
        response = model_client.llm(request)

        # Stop loading animation
        loading.stop()

        reply_text = response["choices"][0]["message"]["content"]

        # Parse the response to get the selected agent's id
        decision_res = string_util.json_loads(reply_text)
        selected_agent_id = decision_res.get("id")  # Extract the id from the response
        subtask = decision_res.get("subtask")

        # Find the selected agent based on the id
        selected_agent: Agent = self.agents[selected_agent_id]
        selected_agent.subtask = subtask

        if selected_agent:
            # Call the selected agent's step method
            selected_agent.step()
        else:
            print("No agent found with the selected id.")

        # Print task completion information
        print(f"Team {self.name} completed the task")


GROUP_DECISION_PROMPT = """## Role
As an expert in team task allocation, your role is to select the most suitable team member to initially address the task at hand, and give the subtask that need to be answered by this member. 
After the task is completed, the results will pass to next member.

## Team
Team Name: {group_name}
Team Description: {group_description}
Team Rules: {group_rules}

## List of team members:
{agents_str}

## User Question:
{user_question}

Please return the result in the following JSON structure which can be parsed directly by json.loads(), no extra content:
{{"id": <member_id>, "subtask": ""}}"""
