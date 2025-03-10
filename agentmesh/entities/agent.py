from agentmesh.models.model_client import ModelClient
from agentmesh.models import LLMRequest
from agentmesh.entities.context import GroupContext
from agentmesh.common.utils import string_util


class Agent:
    def __init__(self, name: str, system_prompt: str, model: str, description: str, group_context=None):
        """
        Initialize the Agent with a name, system prompt, model, description, and optional group context.

        :param name: The name of the agent.
        :param system_prompt: The system prompt for the agent.
        :param model: The model used by the agent.
        :param description: A description of the agent.
        :param group_context: Optional reference to the group context.
        """
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.description = description
        self.group_context: GroupContext = group_context  # Store reference to group context if provided

    def step(self):
        """
        Execute the agent's task by querying the model and deciding on the next steps.

        :param user_question: The question posed by the user.
        """
        model_client = ModelClient()
        
        # First model call to get the response based on user question and system prompt
        prompt = f"{self.system_prompt}\nUser Question: {self.group_context.user_question}"
        request = LLMRequest(model_provider="openai", model=self.model,
                              messages=[{"role": "user", "content": prompt}], 
                              temperature=0, 
                              max_tokens=150,
                              json_format=True)
        response = model_client.call_llm(request)
        reply_text = response["choices"][0]["message"]["content"]
        print(f"{self.name} received response: {reply_text}")
        self.group_context.executed_agents.append(self.name)

        # Logic to decide if another agent is needed
        self.should_invoke_next_agent(reply_text)

    def should_invoke_next_agent(self, reply_text: str) -> bool:
        """
        Determine if the next agent should be invoked based on the reply.

        :param reply_text: The response from the model.
        :return: True if the next agent should be invoked, False otherwise.
        """
        model_client = ModelClient()

        # Create a request to the model to determine if the next agent should be invoked
        agents_str = ', '.join(
            f'{{"id": {i}, "name": "{agent.name}", "description": "{agent.description}", "system_prompt": "{agent.system_prompt}"}}'
            for i, agent in enumerate(self.group_context.agents)
        )
        prompt = AGENT_DECISION_PROMPT.format(group_name=self.group_context.name, group_description=self.group_context.description,
                                              current_agent_name=self.name,
                                              agent_reply=reply_text,
                                              group_rules=self.group_context.rule, execute_agents_name=' -> '.join(self.group_context.executed_agents), agents_str=agents_str,
                                              user_question=self.group_context.user_question)
        print(f"[Think] {self.name} start think...")
        request = LLMRequest(model_provider="openai", model="gpt-4o-mini",
                              messages=[{"role": "user", "content": prompt}], 
                              temperature=0, 
                              max_tokens=10,
                              json_format=True)
        
        response = model_client.call_llm(request)
        decision_text = response["choices"][0]["message"]["content"]
        try:
            selected_agent_id = string_util.json_loads(decision_text).get("id")
            if int(selected_agent_id) < 0:
                print("\n\n[END] User Task Finished")
                return True
            selected_agent: Agent = self.group_context.agents[selected_agent_id]
            print(f"[Think] next agent: {selected_agent.name}")
            selected_agent.step()
        except Exception as e:
            pass
        # Implement your logic to decide if another agent is needed based on the model's decision
        return True


AGENT_DECISION_PROMPT = """## Role
You are an agent team decision expert, Please decision whether the next member in team is needed to complete the user task. If necessary, select the most suitable member, If not, return {{"id": -1}} directly. 

## Team
Team Name: {group_name}
Team Description: {group_description}
Team Rules: {group_rules}

## List of all members:
{agents_str}

## Attention
1. You need to determine whether the next member is needed and which member is the most suitable based on the user's question and the rules of the team 
2. If you think the executed members can satisfy the user's question, return {{"id": -1}} immediately; otherwise, select the next suitable member ID in the following JSON structure which can be parsed directly by json.loads(): {{"id": <member_id>}}

## Members that have been executed:
{execute_agents_name}

## User Question:
{user_question}"""
