<p align="center"><img src= "https://github.com/user-attachments/assets/743bb0da-3070-4e89-b744-e7b3ab886fe8" alt="AgentMesh" width="450" /></p>

English | <a href="/docs/README-CN.md">中文</a>

AgentMesh is a **Multi-Agent platform** for AI agents building, providing a framework for inter-agent communication,
task planning, and autonomous decision-making. Build your agent team quickly and solve complex tasks through agent
collaboration.

## Overview

AgentMesh uses a modular layered design for flexible and extensible multi-agent systems:

- **Agent Collaboration**: Support for role definition, task allocation, and multi-turn autonomous decision-making.
  Communication protocol for remote heterogeneous agents coming soon.
- **Multi-Modal Models**: Seamless integration with OpenAI, Claude, DeepSeek, and other leading LLMs through a unified
  API.
- **Extensible Tools**: Built-in search engines, browser automation, file system access, and terminal tools. MCP
  protocol support coming soon for even more tool extensions.
- **Multi-Platform**: Run via CLI, Docker, or SDK. WebUI and integration with common software coming soon.

## Quick Start

Choose one of these three ways to build and run your agent team:

### 1. Terminal

Run a multi-agent team from your command line:

#### 1.1 Installation

**Requirements:** Linux, MacOS, or Windows with Python installed.

> Python 3.11+ recommended (especially for browser tools), at least python 3.7+ required.
> Download from: [Python.org](https://www.python.org/downloads/).

Clone the repo and navigate to the project:

```bash
git clone https://github.com/MinimalFuture/AgentMesh
cd AgentMesh
```

Install core dependencies:

```bash
pip install -r requirements.txt
```

For browser tools, install additional dependencies (python3.11+ required):

```bash
pip install browser-use
playwright install
```

#### 1.2 Configuration

Edit the `config.yaml` file with your model settings and agent configurations:

```bash
cp config-template.yaml config.yaml
```

Add your model `api_key` - AgentMesh supports `openai`, `claude`, `deepseek`, `qwen`, and others.

The template includes two examples for quick testing:

- `general_team`: A single general-purpose agent skilled in search, research, and information organization. Recommended to configure with google_search and browser tools.
- `software_team`: A development team with three roles (product manager, engineer, and tester) that can collaborate on web application development and testing tasks, delivering complete project documentation and code.

You can modify the template to customize different models, tools, system prompts, and other configurations for each agent.

#### 1.3 Execution

You can run tasks directly using command-line arguments, specifying the team with `-t` and your question with `-q`:

```bash
python main.py -t general_team -q "analyze the trends in multi-agent technology"
python main.py -t software_team -q "develop a simple trial booking page for AgentMesh multi-agent platform"
```

Alternatively, enter interactive mode for multi-turn conversations:

```bash
python main.py -l                               # List available agent teams
python main.py -t software_team                 # Run the 'software_team'
```

### 2. Docker

Download the docker-compose configuration file:

```bash
curl -O https://raw.githubusercontent.com/MinimalFuture/AgentMesh/main/docker-compose.yml
```

Download the configuration template and add your model API keys (see section 1.2 for configuration details):

```bash
curl -o config.yaml https://raw.githubusercontent.com/MinimalFuture/AgentMesh/main/config-template.yaml
```

Run the Docker container:

```bash
docker-compose run --rm agentmesh bash
```

Once the container starts, you'll enter the command line. The usage is the same as in section 1.3 - specify a team to start the interactive mode:

```bash
python main.py -l                               # List available agent teams
python main.py -t general_team                  # Start multi-turn conversation with the specified team
```

### 3. SDK

Use the AgentMesh SDK to build custom agent teams programmatically:

```bash
pip install agentmesh-sdk
```

Example usage (replace `YOUR_API_KEY` with your actual API key):

```python
from agentmesh import AgentTeam, Agent, LLMModel
from agentmesh.tools import *

# Initialize model
model = LLMModel(model="gpt-4.1", api_key="YOUR_API_KEY")

# Create team and add agents
team = AgentTeam(name="software_team", description="A software development team", model=model)

team.add(Agent(name="PM", description="Handles product requirements",
               system_prompt="You are an experienced PM who creates clear, comprehensive PRDs"))

team.add(Agent(name="Developer", description="Implements code based on requirements", model=model,
               system_prompt="You write clean, efficient, maintainable code following requirements precisely",
               tools=[Calculator(), GoogleSearch()]))

# Execute task
result = team.run(task="Write a Snake client game")
```

### 4. Web Service

Coming soon

## Components

### Core Concepts

- **Agent**: Autonomous decision-making unit with specific roles and capabilities, configurable with models, system
  prompts, tools, and decision logic.
- **AgentTeam**: Team of agents responsible for task allocation, context management, and collaboration workflow.
- **Tool**: Functional modules that extend agent capabilities, such as calculators, search engines, and browsers.
- **Task**: User input problems or requirements, which can include text, images, and other multi-modal content.
- **Context**: Shared information including team details, task content, and execution history.
- **LLMModel**: Large language model interface supporting various mainstream LLMs through a unified API.

### Supported Models

- **OpenAI**: GPT series models, recommended: `gpt-4.1`, `gpt-4o`, `gpt-4.1-mini`
- **Claude**: Claude series models, recommended: `claude-3-7-sonnet-latest`
- **DeepSeek**: DeepSeek series models, recommended: `deepseek-chat`
- **Ollama**: Local open-source models (coming soon)

### Built-in Tools

- **calculator**: Mathematical calculation tool supporting complex expression evaluation
- **current_time**: Current time retrieval tool solving model time awareness issues
- **browser**: Web browsing tool based on browser-use, supporting web access, content extraction, and interaction
- **google_search**: Search engine tool for retrieving up-to-date information
- **MCP**: Extended tool capabilities through MCP protocol support (coming soon)

## Contribution

⭐️ Star this project to receive notifications about updates.

Feel free to [submit PRs](https://github.com/MinimalFuture/AgentMesh/pulls) to contribute to this project.
For issues or ideas, please [open an issue](https://github.com/MinimalFuture/AgentMesh/issues).
