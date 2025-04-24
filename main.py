import argparse

from agentmesh.common import logger
from agentmesh.common import load_config, config, ModelFactory
from agentmesh.protocal import AgentTeam, Agent, Task
from agentmesh.tools.tool_manager import ToolManager


def create_team_from_config(team_name):
    """Create a team from configuration."""
    # Get teams configuration
    teams_config = config().get("teams", {})

    # Check if the specified team exists
    if team_name not in teams_config:
        print(f"Error: Team '{team_name}' not found in configuration.")
        available_teams = list(teams_config.keys())
        print(f"Available teams: {', '.join(available_teams)}")
        return None

    # Get team configuration
    team_config = teams_config[team_name]

    # Initialize ModelFactory
    model_factory = ModelFactory()

    # Get team's model
    team_model_name = team_config.get("model", "gpt-4o")
    team_model = model_factory.get_model(team_model_name)

    # Get team's max_steps (default to 20 if not specified)
    team_max_steps = team_config.get("max_steps", 20)

    # Create team with the model
    team = AgentTeam(
        name=team_name,
        description=team_config.get("description", ""),
        rule=team_config.get("rule", ""),
        model=team_model,
        max_steps=team_max_steps
    )

    # Create and add agents to the team
    agents_config = team_config.get("agents", [])
    for agent_config in agents_config:
        # Check if agent has a specific model
        if agent_config.get("model"):
            agent_model = model_factory.get_model(agent_config.get("model"))
        else:
            agent_model = team_model

        # Get agent's max_steps
        agent_max_steps = agent_config.get("max_steps")

        agent = Agent(
            name=agent_config.get("name", ""),
            system_prompt=agent_config.get("system_prompt", ""),
            model=agent_model,  # Use agent's model if specified, otherwise will use team's model
            description=agent_config.get("description", ""),
            max_steps=agent_max_steps
        )

        # Add tools to the agent if specified
        tool_names = agent_config.get("tools", [])
        tool_manager = ToolManager()
        for tool_name in tool_names:
            tool = tool_manager.create_tool(tool_name)
            if tool:
                agent.add_tool(tool)
            else:
                if tool_name == "browser":
                    logger.warning(
                        "Tool 'Browser' loaded failed, "
                        "please install the required dependency with: \n"
                        "'pip install browser-use>=0.1.40' or 'pip install agentmesh-sdk[full]'\n"
                    )
                else:
                    logger.warning(f"Tool '{tool_name}' not found for agent '{agent.name}'\n")

        # Add agent to team
        team.add(agent)

    return team


def list_available_teams():
    """List all available teams from configuration."""
    teams_config = config().get("teams", {})
    if not teams_config:
        print("No teams found in configuration.")
        return

    print("Available teams:")
    for team_name, team_config in teams_config.items():
        print(f"  - {team_name}: {team_config.get('description', '')}")


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="AgentMesh - Multi-Agent Framework")
    parser.add_argument("-t", "--team", help="Specify the team to run")
    parser.add_argument("-l", "--list", action="store_true", help="List available teams")
    parser.add_argument("-q", "--query", help="Direct query to run (non-interactive mode)")
    args = parser.parse_args()

    # Load configuration
    load_config()

    # Load tools
    ToolManager().load_tools()

    # List teams if requested
    if args.list:
        list_available_teams()
        return

    # If no team is specified, show usage
    if not args.team:
        parser.print_help()
        return

    # Create team from configuration
    team = create_team_from_config(args.team)
    if not team:
        return

    # If a direct query is provided, run it in non-interactive mode
    if args.query:
        print(f"Team '{team.name}' loaded successfully.")
        print(f"User task: {args.query}")
        print()

        # Run the team with the user's query
        team.run(Task(content=args.query), output_mode="print")
        return

    # Otherwise, run in interactive mode
    print(f"Team '{team.name}' loaded successfully.")
    print(f"Description: {team.description}")
    print(f"Number of agents: {len(team.agents)}")
    print("\nEnter your task (type 'exit' to quit):")

    count = 0
    # Interactive loop
    while True:
        try:
            if count > 0:
                team = create_team_from_config(args.team)
            count += 1
            user_input = input("> ")
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting AgentMesh. Goodbye!")
                break

            if user_input.strip():
                # Run the team with the user's task
                team.run(Task(content=user_input), output_mode="print")
                print("\nEnter your next task (type 'exit' to quit):")
        except KeyboardInterrupt:
            print("\nExiting AgentMesh. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
