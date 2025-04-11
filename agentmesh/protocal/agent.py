import json
import time

from agentmesh.common import LoadingIndicator
from agentmesh.common.utils import string_util
from agentmesh.common.utils.xml_util import XmlResParser
from agentmesh.models import LLMRequest, LLMModel
from agentmesh.models.model_factory import ModelFactory
from agentmesh.protocal.context import TeamContext, AgentOutput
from agentmesh.tools.base_tool import BaseTool


class Agent:
    def __init__(self, name: str, system_prompt: str, description: str, model: LLMModel = None, team_context=None):
        """
        Initialize the Agent with a name, system prompt, model, description, and optional group context.

        :param name: The name of the agent.
        :param system_prompt: The system prompt for the agent.
        :param model: An instance of LLMModel to be used by the agent.
        :param description: A description of the agent.
        :param team_context: Optional reference to the group context.
        """
        self.name = name
        self.system_prompt = system_prompt
        self.model: LLMModel = model  # Instance of LLMModel
        self.description = description
        self.team_context: TeamContext = team_context  # Store reference to group context if provided
        self.subtask: str = ""
        self.tools: list = []
        self.max_react_steps = 20  # max ReAct steps
        self.conversation_history = []
        self.action_history = []
        self.ext_data = ""

    def add_tool(self, tool: BaseTool):
        self.tools.append(tool)

    def _build_tools_prompt(self) -> str:
        """Build the tool list description"""
        return "\n".join([
            f"{tool.name}: {tool.description} (parameters: {tool.params})"
            for tool in self.tools
        ])

    def _build_react_prompt(self) -> str:
        """Build the initial prompt template"""
        tools_list = self._build_tools_prompt()

        # Get the current timestamp
        timestamp = time.time()

        # Convert the timestamp to local time
        local_time = time.localtime(timestamp)

        # Format the time
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        ext_data_prompt = self.ext_data

        tools_prompt = f"""## Role
Your role: {self.name}
Your role description: {self.description}
You are handling the subtask: {self.subtask}, as a member of the {self.team_context.name} team. Please answer in the same language as the user's original task.

## Available tools
{tools_list}

## Reply format 
Please respond strictly in the following format:
<thought> Analyze the current situation and the next action </thought>
<action> Tool name, must be one of available tools. The value can be null when final_answer is obtained </action>
<action_input> Tool parameters in JSON format </action_input>
<final_answer> The final answer should be as detailed and rich as possible. If there is no final answer, do not show this label </final_answer>

## Attention
The content of thought and final_answer needs to be consistent with the language used by the user original task.
"""

        current_task_prompt = f"""
## Current task context:
Current time: {formatted_time}
Team description: {self.team_context.description}
Other agents output: {self._fetch_agents_outputs()}

User origin task: {self.team_context.user_task}
Your sub task: {self.subtask}"""

        return tools_prompt + ext_data_prompt + current_task_prompt

    def _find_tool(self, tool_name: str):
        for tool in self.tools:
            if tool.name == tool_name:
                return tool

    def step(self):
        """
        Execute the agent's task by querying the model and deciding on the next steps.
        """
        final_answer = None
        current_step = 0
        raw_response = ""

        # Print agent name and subtask
        print(f"🤖 {self.name.strip()}: {self.subtask}")

        while current_step < self.max_react_steps and not final_answer:
            user_prompt = self._build_react_prompt() + "\n\n## Historical steps:\n"
            if self.action_history:
                user_prompt += f"\n{json.dumps(self.action_history[-5:], ensure_ascii=False, indent=4)}"
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # Get the model to use - use agent's model if set, otherwise use team's model
            model_to_use = self.model if self.model else self.team_context.model

            # Generate model request
            request = LLMRequest(
                messages=messages,
                temperature=0,
                max_tokens=500,
                json_format=False,
                stream=True
            )

            # Start loading animation before getting model response
            print()
            loading = LoadingIndicator(message="Thinking...", animation_type="spinner")
            loading.start()

            # Get model response directly from the model instance
            stream_response = model_to_use.call_stream(request)
            parser = XmlResParser()
            raw_response = ""
            # Create element display area

            first_token = True
            for chunk in stream_response:
                if first_token:
                    first_token = False
                    loading.stop()
                    print(f"Step {current_step + 1}:")

                # Ensure chunk is in the correct format
                if isinstance(chunk, dict):
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0].get("delta", {})
                        if "content" in delta:
                            content = delta["content"]
                            raw_response += content
                            # Use parser to process each streaming content chunk
                            parser.process_chunk(content)
                else:
                    # If chunk is a string, process it directly
                    raw_response += chunk
                    parser.process_chunk(chunk)

            # Get parsing results
            parsed = parser.get_parsed_data()

            # Handle final answer
            if "final_answer" in parsed and parsed["final_answer"] and parsed["final_answer"].lower() != "null":
                final_answer = parsed["final_answer"]
                break

            # Handle tool invocation
            if "action" in parsed and parsed["action"] and parsed["action"].lower() != "null":
                # Execute tool
                tool: BaseTool = self._find_tool(parsed["action"])
                observation = ""
                if tool:
                    tool_result = tool.execute_tool(parsed.get("action_input", {}))
                    # Update conversation history
                    parsed["Observation"] = {
                        "status": tool_result.status,
                        "result": tool_result.result
                    }
                    if tool_result.ext_data:
                        self.ext_data = tool_result.ext_data
                self.action_history.append(parsed)
                self.conversation_history.append({
                    "role": "assistant",
                    "content": f"Thought: {parsed.get('thought', '')}\n"
                               f"Action: {parsed['action']}\n"
                               f"Action Input: {json.dumps(parsed.get('action_input', {}))}"
                })
                if observation:
                    # print(f"\n📊 Observation: {observation}")
                    self.conversation_history.append({
                        "role": "user",
                        "content": f"Observation: {observation}"
                    })
            else:
                # No action, end loop
                break

            current_step += 1

        # Save final result
        result = final_answer if final_answer else raw_response
        self.team_context.agent_outputs.append(
            AgentOutput(agent_name=self.name, output=result)
        )

        # Decide whether to invoke another agent
        self.should_invoke_next_agent()

    def should_invoke_next_agent(self) -> bool:
        """
        Determine if the next agent should be invoked based on the reply.

        :return: True if the next agent should be invoked, False otherwise.
        """
        # Get the model to use - use team's model
        model_to_use = self.team_context.model

        # Create a request to the model to determine if the next agent should be invoked
        agents_str = ', '.join(
            f'{{"id": {i}, "name": "{agent.name}", "description": "{agent.description}", "system_prompt": "{agent.system_prompt}"}}'
            for i, agent in enumerate(self.team_context.agents)
        )
        agent_outputs_list = self._fetch_agents_outputs()

        prompt = AGENT_DECISION_PROMPT.format(group_name=self.team_context.name,
                                              group_description=self.team_context.description,
                                              current_agent_name=self.name,
                                              group_rules=self.team_context.rule,
                                              agent_outputs_list=agent_outputs_list, agents_str=agents_str,
                                              user_task=self.team_context.user_task)

        # Start loading animation
        print()
        loading = LoadingIndicator(message="Select agent in team...", animation_type="spinner")
        loading.start()

        # Use team's model for agent selection decision
        request = LLMRequest(
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            json_format=True
        )

        response = model_to_use.call(request)

        # Stop loading animation
        loading.stop()
        print()

        decision_text = response["choices"][0]["message"]["content"]
        try:
            decision_res = string_util.json_loads(decision_text)
            selected_agent_id = decision_res.get("id")
            
            # Check if we should stop the chain
            if selected_agent_id is None or int(selected_agent_id) < 0:
                return False
            
            # Get subtask
            subtask = decision_res.get("subtask", "")
            
            # Prevent self-recursion - don't allow an agent to call itself
            if int(selected_agent_id) >= 0 and int(selected_agent_id) < len(self.team_context.agents):
                selected_agent = self.team_context.agents[int(selected_agent_id)]
                # Check if the selected agent is the current agent
                if selected_agent.name == self.name:
                    print(f"\n[Warning] Agent '{self.name}' attempted to call itself. Stopping chain.")
                    return False
                
                # Set subtask and call the next agent
                selected_agent.subtask = subtask
                print()
                selected_agent.step()
                return True
            else:
                print(f"\n[Warning] Invalid agent ID: {selected_agent_id}")
                return False
        except Exception as e:
            print(f"\n[Error] Failed to determine next agent: {e}")
            return False

    def _fetch_agents_outputs(self) -> str:
        agent_outputs_list = []
        for agent_output in self.team_context.agent_outputs:
            agent_outputs_list.append(
                f"member name: {agent_output.agent_name}\noutput content: {agent_output.output}\n\n")
        return "\n".join(agent_outputs_list)


AGENT_REPLY_PROMPT = """You are part of the team, you only need to reply the part of user question related to your responsibilities

## Team
Team Name: {group_name}
Team Description: {group_description}
Team Rules: {group_rules}
Your Role: {current_agent_name}

## Team members have already output
{agent_outputs_list}

User Original Task: 
{user_task}

Your Subtask:
{subtask}"""

AGENT_DECISION_PROMPT = """## Role
You are a team decision expert, please decide whether the next member in the team is needed to complete the user task. If necessary, select the most suitable member and give the subtask that needs to be answered by this member. If not, return {{"id": -1}} directly.

## Team
Team Name: {group_name}
Team Description: {group_description}
Team Rules: {group_rules}

## List of all members:
{agents_str}

## Members have replied
{agent_outputs_list}

## Attention
1. You need to determine whether the next member is needed and which member is the most suitable based on the user's question and the rules of the team 
2. If you think the answers given by the executed members are able to answer the user's questions, return {{"id": -1}} immediately; otherwise, select the next suitable member ID and subtask content in the following JSON structure which can be parsed directly by json.loads(): 
{{"id": <member_id>, "subtask": ""}}
3. Always reply in JSON format which can be parsed directly by json.loads()

## User Original Task:
{user_task}"""
