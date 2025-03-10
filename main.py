from agentmesh.common import config, load_config
from agentmesh.entities import AgentTeam, Agent


def test_case():
    team = AgentTeam(name="A software team", description="A software team",
                       rule="The product manager is responsible for writing the PRD, the coder is responsible for writes the code according to PRD")
    team.add_agent(Agent(name="coder", description="A coder", model="deepseek-chat", system_prompt="You are a programmer who writes elegant code."))
    team.add_agent(Agent(name="PM", description="A product manager", model="deepseek-chat", system_prompt="You are a product manager who writes PRD (Product Requirements Document)"))
    team.run(user_question="Design and implement a user login module in python")

def run():
    load_config()
    test_case()


if __name__ == "__main__":
    run()
