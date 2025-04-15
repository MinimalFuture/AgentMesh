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

> The template includes a pre-configured `software_team` with three roles (PM, architect, engineer) that collaborate on
> software development tasks.

#### 1.3 Execution

```bash
python main.py -l                   # List available agent teams
python main.py -t software_team     # Run the 'software_team'
```

Enter your requirements in the interactive prompt to begin.

### 2. SDK

Use the AgentMesh SDK to build custom agent teams programmatically:

```bash
pip install agentmesh-sdk
```

Example usage (replace `YOUR_API_KEY` with your actual API key):

```python
from agentmesh import AgentTeam, Agent, LLMModel
from agentmesh.tools import *

# Initialize model
model = LLMModel(model="gpt-4o", api_key="YOUR_API_KEY")

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

### 3. Web Service

Coming soon

## Details

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
- **MCP**: Multi-modal content processing tool supporting image recognition and generation (coming soon)

## Contribution

Star this project to receive notifications about updates.

Feel free to [submit PRs](https://github.com/MinimalFuture/AgentMesh/pulls) to contribute to this project.
For issues or ideas, please [open an issue](https://github.com/MinimalFuture/AgentMesh/issues).
