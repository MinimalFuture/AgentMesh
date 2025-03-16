from agentmesh.models.model_client import ModelClient
from agentmesh.models import LLMRequest
from agentmesh.entities.context import TeamContext, AgentOutput
from agentmesh.common.utils import string_util
from agentmesh.tools.base_tool import BaseTool
import json


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
        self.group_context: TeamContext = group_context  # Store reference to group context if provided
        self.subtask: str = ""
        self.tools: list = []
        self.max_react_steps = 5     # max ReAct steps
        self.conversation_history = []

    def add_tool(self, tool: BaseTool):
        self.tools.append(tool)

    def _build_tools_prompt(self) -> str:
        """构建工具列表描述"""
        return "\n".join([
            f"{tool.name}: {tool.description} (参数: {tool.args_schema})"
            for tool in self.tools
        ])

    def _build_initial_prompt(self) -> str:
        """构建初始提示模板"""
        tools_list = self._build_tools_prompt()

        return f"""You are handling the subtask: {self.subtask}, as a member of the {self.group_context.name} team.
Available tools:
{tools_list}

Please respond strictly in the following format:
{{
  "thought": "Analyze the current situation and the next action",
  "action": "Tool name or null",
  "action_input": {{parameters}},
  "final_answer": "Final answer or null"
}}

Current task context:
Team Description: {self.group_context.description}
User Original task: {self.group_context.user_task}
Historical steps: {self._fetch_agents_outputs()}
"""

    def _parse_response(self, response: str) -> dict:
        """解析模型响应，支持多种格式"""
        try:
            # 优先尝试JSON解析
            return json.loads(response)
        except json.JSONDecodeError:
            pass

    def _find_tool(self, tool_name: str):
        for tool in self.tools:
            if tool.name == tool_name:
                return tool

    def step(self):
        """
        Execute the agent's task by querying the model and deciding on the next steps.
        """
        model_client = ModelClient()

        # First model call to get the response based on user question and system prompt
        """执行ReACT推理循环"""
        model_client = ModelClient()
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self._build_initial_prompt()}
        ]

        final_answer = None
        current_step = 0
        raw_response = ""

        while current_step < self.max_react_steps and not final_answer:
            # 生成模型请求
            request = LLMRequest(
                model_provider="openai",
                model=self.model,
                messages=self.conversation_history,
                temperature=0,
                max_tokens=500,
                json_format=True
            )

            # 获取模型响应
            response = model_client.llm(request)
            raw_response = response["choices"][0]["message"]["content"]
            print(f"[{self.name}] Step {current_step + 1} Response:\n{raw_response}")

            # 解析响应内容
            parsed = self._parse_response(raw_response)

            # 处理最终答案
            if "final_answer" in parsed and parsed["final_answer"]:
                final_answer = parsed["final_answer"]
                break

            # 处理工具调用
            if "action" in parsed and parsed["action"]:
                # 执行工具
                tool: BaseTool = self._find_tool(parsed["action"])
                observation = tool.execute(
                    parsed.get("action_input", {})
                )
                # 更新对话历史
                self.conversation_history.append({
                    "role": "assistant",
                    "content": f"Thought: {parsed.get('thought', '')}\n"
                               f"Action: {parsed['action']}\n"
                               f"Action Input: {json.dumps(parsed.get('action_input', {}))}"
                })

                self.conversation_history.append({
                    "role": "user",
                    "content": f"Observation: {observation}"
                })
            else:
                # 没有动作则结束循环
                break

            current_step += 1

        # 保存最终结果
        result = final_answer if final_answer else raw_response
        self.group_context.agent_outputs.append(
            AgentOutput(agent_name=self.name, output=result)
        )
        print(f"[{self.name}] Final Output: {result}")
        print(f"{self.name} agent reply: {result}")
        
        self.group_context.agent_outputs.append(AgentOutput(agent_name=self.name, output=result))

        # Logic to decide if another agent is needed
        self.should_invoke_next_agent()

    def should_invoke_next_agent(self) -> bool:
        """
        Determine if the next agent should be invoked based on the reply.

        :return: True if the next agent should be invoked, False otherwise.
        """
        model_client = ModelClient()

        # Create a request to the model to determine if the next agent should be invoked
        agents_str = ', '.join(
            f'{{"id": {i}, "name": "{agent.name}", "description": "{agent.description}", "system_prompt": "{agent.system_prompt}"}}'
            for i, agent in enumerate(self.group_context.agents)
        )
        agent_outputs_list = self._fetch_agents_outputs()

        prompt = AGENT_DECISION_PROMPT.format(group_name=self.group_context.name,
                                              group_description=self.group_context.description,
                                              current_agent_name=self.name,
                                              group_rules=self.group_context.rule,
                                              agent_outputs_list=agent_outputs_list, agents_str=agents_str,
                                              user_task=self.group_context.user_task)
        print(f"[Think] {self.name} start think...")
        request = LLMRequest(model_provider="openai", model="gpt-4o-mini",
                             messages=[{"role": "user", "content": prompt}],
                             temperature=0,
                             max_tokens=10,
                             json_format=True)

        response = model_client.llm(request)
        decision_text = response["choices"][0]["message"]["content"]
        try:
            decision_res = string_util.json_loads(decision_text)
            selected_agent_id = string_util.json_loads(decision_text).get("id")
            subtask = decision_res.get("subtask")
            if int(selected_agent_id) < 0:
                print("[END] User Task Finished")
                return True
            selected_agent: Agent = self.group_context.agents[selected_agent_id]
            selected_agent.subtask = subtask
            print(f"[Think] next agent: {selected_agent.name}, subtask: {subtask}")
            selected_agent.step()
        except Exception as e:
            pass
        # Implement your logic to decide if another agent is needed based on the model's decision
        return True

    def _fetch_agents_outputs(self) -> str:
        agent_outputs_list = []
        for agent_output in self.group_context.agent_outputs:
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
You are an team decision expert, Please decision whether the next member in team is needed to complete the user task. If necessary, select the most suitable member and give the subtask that need to be answered by this member, If not, return {{"id": -1}} directly. 

## Team
Team Name: {group_name}
Team Description: {group_description}
Team Rules: {group_rules}

## List of all members:
{agents_str}

## Attention
1. You need to determine whether the next member is needed and which member is the most suitable based on the user's question and the rules of the team 
2. If you think the answers given by the executed members are able to answer the user's questions, return {{"id": -1}} immediately; otherwise, select the next suitable member ID and subtask content in the following JSON structure which can be parsed directly by json.loads(): 
{{"id": <member_id>, "subtask": ""}}

## Members have replied
{agent_outputs_list}

## User Original Task:
{user_task}"""
