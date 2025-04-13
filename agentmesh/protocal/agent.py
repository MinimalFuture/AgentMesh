import json
import time

from agentmesh.common import LoadingIndicator
from agentmesh.common.utils import string_util
from agentmesh.common.utils.log import logger
from agentmesh.common.utils.xml_util import XmlResParser
from agentmesh.models import LLMRequest, LLMModel
from agentmesh.protocal.context import TeamContext, AgentOutput
from agentmesh.protocal.result import AgentAction, AgentActionType, ToolResult
from agentmesh.tools.base_tool import BaseTool


class Agent:
    def __init__(self, name: str, system_prompt: str, description: str, model: LLMModel = None, team_context=None,
                 tools=None, output_mode="print"):
        """
        Initialize the Agent with a name, system prompt, model, description, and optional group context.

        :param name: The name of the agent.
        :param system_prompt: The system prompt for the agent.
        :param model: An instance of LLMModel to be used by the agent.
        :param description: A description of the agent.
        :param team_context: Optional reference to the group context.
        :param tools: Optional list of tools for the agent to use.
        :param output_mode: Control how execution progress is displayed: 
                           "print" for console output or "logger" for using logger
        """
        self.name = name
        self.system_prompt = system_prompt
        self.model: LLMModel = model  # Instance of LLMModel
        self.description = description
        self.team_context: TeamContext = team_context  # Store reference to group context if provided
        self.subtask: str = ""
        self.tools: list = []
        self.max_react_steps = 10  # max ReAct steps
        self.conversation_history = []
        self.action_history = []
        self.ext_data = ""
        self.output_mode = output_mode
        if tools:
            for tool in tools:
                self.add_tool(tool)

    def add_tool(self, tool: BaseTool):
        tool.model = self.model
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
                tool.model = self.model
                return tool

    # output function based on mode
    def output(self, message="", end="\n"):
        if self.output_mode == "print":
            print(message, end=end)
        elif message:
            logger.info(message)

    def step(self):
        """
        Execute the agent's task by querying the model and deciding on the next steps.
        """
        final_answer = None
        current_step = 0
        raw_response = ""

        # 初始化捕获的动作列表（如果不存在）
        if not hasattr(self, 'captured_actions'):
            self.captured_actions = []

        # 初始化最终答案（如果不存在）
        if not hasattr(self, 'final_answer'):
            self.final_answer = ""

        # Print agent name and subtask
        self.output(f"🤖 {self.name.strip()}: {self.subtask}")

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
                json_format=False,
                stream=self.output_mode == "print"  # Only stream in print mode
            )

            # Start loading animation before getting model response (only in print mode)
            loading = None
            if self.output_mode == "print":
                print()
                loading = LoadingIndicator(message="Thinking...", animation_type="spinner")
                loading.start()

            # Get model response based on output mode
            if self.output_mode == "print":
                # Stream response in print mode
                stream_response = model_to_use.call_stream(request)
                parser = XmlResParser()
                raw_response = ""

                first_token = True
                for chunk in stream_response:
                    # Check if this is an error chunk
                    if isinstance(chunk, dict) and chunk.get("error", False):
                        if loading:
                            loading.stop()
                        error_message = chunk.get("message", "Unknown error")
                        status_code = chunk.get("status_code", 0)
                        # Use logger to record errors, no need to duplicate printing
                        logger.error(f"Error: {error_message} (Status code: {status_code})")
                        return f"Error: {error_message}"

                    if first_token:
                        first_token = False
                        if loading:
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
            else:
                # Non-streaming mode for logger
                response = model_to_use.call(request)

                # Check if the API call was successful
                if response.is_error:
                    error_message = response.get_error_msg()
                    # Use logger to record errors, no need to duplicate printing
                    logger.error(f"Error: {error_message}")
                    return f"Error: {error_message}"

                raw_response = response.data["choices"][0]["message"]["content"]

                # Parse the response
                parser = XmlResParser()
                parser.process_chunk(raw_response)
                parsed = parser.get_parsed_data()

                # Log the parsed data in a structured way
                if "thought" in parsed:
                    logger.info(f"🧠 {parsed['thought']}")
                if "action" in parsed and parsed["action"] and parsed["action"].lower() != "null":
                    action_input = parsed.get("action_input", {})
                    action_input_str = json.dumps(action_input, ensure_ascii=False) if action_input else ""
                    logger.info(f"🛠️ {parsed['action']}: {action_input_str}")
                if "final_answer" in parsed and parsed["final_answer"] and parsed["final_answer"].lower() != "null":
                    logger.info(f"💬 {parsed['final_answer']}")

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

                    # Log tool execution errors
                    if tool_result.status == "error":
                        logger.error(f"Tool execution error: {tool_result.result}")

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
        self.final_answer = result
        self.team_context.agent_outputs.append(
            AgentOutput(agent_name=self.name, output=result)
        )

        return self.final_answer

    def should_invoke_next_agent(self) -> int:
        """
        Determine if the next agent should be invoked based on the reply.

        :return: The ID of the next agent to invoke, or -1 if no next agent should be invoked.
        """
        # Get the model to use - use team's model
        model_to_use = self.team_context.model

        # Create a request to the model to determine if the next agent should be invoked
        # Exclude the current agent from the list to prevent self-recursion
        agents_str = ', '.join(
            f'{{"id": {i}, "name": "{agent.name}", "description": "{agent.description}", "system_prompt": "{agent.system_prompt}"}}'
            for i, agent in enumerate(self.team_context.agents)
            if agent.name != self.name  # Exclude current agent
        )

        # If no other agents are available, return -1
        if not agents_str:
            return -1

        agent_outputs_list = self._fetch_agents_outputs()

        prompt = AGENT_DECISION_PROMPT.format(group_name=self.team_context.name,
                                              group_description=self.team_context.description,
                                              current_agent_name=self.name,
                                              group_rules=self.team_context.rule,
                                              agent_outputs_list=agent_outputs_list,
                                              agents_str=agents_str,
                                              user_task=self.team_context.user_task)

        # Start loading animation
        self.output()
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

        # Check if API call was successful
        if response.is_error:
            error_message = response.get_error_msg()
            logger.error(f"Error: {error_message}")
            return -1  # If error occurs, return -1 to indicate not to call the next agent

        # Get content from successful response
        decision_text = response.data["choices"][0]["message"]["content"]
        try:
            decision_res = string_util.json_loads(decision_text)
            selected_agent_id = decision_res.get("id")

            # Check if we should stop the chain
            if selected_agent_id is None or int(selected_agent_id) < 0:
                return -1

            # Get subtask
            subtask = decision_res.get("subtask", "")

            # Map the selected agent ID to the actual agent ID
            selected_agent = self.team_context.agents[int(selected_agent_id)]

            # Set subtask for the next agent
            selected_agent.subtask = subtask

            # Return the ID of the next agent
            return int(selected_agent_id)
        except Exception as e:
            logger.error(f"Failed to determine next agent: {e}")
            return -1

    def _fetch_agents_outputs(self) -> str:
        agent_outputs_list = []
        for agent_output in self.team_context.agent_outputs:
            agent_outputs_list.append(
                f"member name: {agent_output.agent_name}\noutput content: {agent_output.output}\n\n")
        return "\n".join(agent_outputs_list)

    def capture_tool_use(self, tool_name, input_params, output, status, error_message=None, execution_time=0.0):
        """
        Capture a tool use action.
        
        :param tool_name: Name of the tool used
        :param input_params: Parameters passed to the tool
        :param output: Output from the tool
        :param status: Status of the tool execution
        :param error_message: Error message if the tool execution failed
        :param execution_time: Time taken to execute the tool
        """
        tool_result = ToolResult(
            tool_name=tool_name,
            input_params=input_params,
            output=output,
            status=status,
            error_message=error_message,
            execution_time=execution_time
        )

        action = AgentAction(
            agent_id=self.id if hasattr(self, 'id') else str(id(self)),
            agent_name=self.name,
            action_type=AgentActionType.TOOL_USE,
            tool_result=tool_result
        )

        if not hasattr(self, 'captured_actions'):
            self.captured_actions = []

        self.captured_actions.append(action)

        return action

    def capture_thinking(self, thought_content):
        """
        Capture a thinking action.
        
        :param thought_content: Content of the thought
        """
        action = AgentAction(
            agent_id=self.id if hasattr(self, 'id') else str(id(self)),
            agent_name=self.name,
            action_type=AgentActionType.THINKING,
            content=thought_content
        )

        if not hasattr(self, 'captured_actions'):
            self.captured_actions = []

        self.captured_actions.append(action)

        return action

    def capture_final_answer(self, answer_content):
        """
        Capture a final answer action.
        
        :param answer_content: Content of the final answer
        """
        action = AgentAction(
            agent_id=self.id if hasattr(self, 'id') else str(id(self)),
            agent_name=self.name,
            action_type=AgentActionType.FINAL_ANSWER,
            content=answer_content
        )

        if not hasattr(self, 'captured_actions'):
            self.captured_actions = []

        self.captured_actions.append(action)

        return action


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
