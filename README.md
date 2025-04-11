<p align="center"><img src= "https://github.com/user-attachments/assets/60534980-ac81-475f-9462-d2205c085028" alt="Chatgpt-on-Wechat" width="500" /></p>

English | <a href="/docs/README-CN.md">中文</a>

AgentMesh is a **Multi-Agent platform** that provides an AI Agent development framework, communication protocols between multiple Agents, complex task planning, and autonomous decision-making. With this platform, you can quickly build your Agent Team to accomplish tasks through collaboration between Agents.

# Quick Start

There are three ways to quickly build and run your Agent Team:

## 1. Terminal Execution

Run a multi-agent team in the terminal command line:

### 1.1 Installation

Download the source code and enter the project directory:

```bash
git clone https://github.com/MinimalFuture/AgentMesh
cd AgentMesh
```

Install Python 3.7 or above, Python 3.11+ is recommended (browser tools require Python 3.11+).

We recommend using the Python virtual environment tool `uv` for one-click installation and execution. First, download uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create a virtual environment:

```bash
uv venv --python 3.11
source .venv/bin/activate
```

Install dependencies:

```bash
pip install requirements.txt
```

### 1.2 Configuration

The configuration file is `config.yaml` in the root directory, which includes model configuration and Agent configuration. You can copy from the template file and modify it:

```bash
cp config-template.yaml config.yaml
```

Fill in the `api_key` for the models you need. AgentMesh supports `openai`, `claude`, `deepseek`, and other models.

The configuration template includes a pre-configured Agent development team called `software_team`, which consists of three roles: product manager, architect, and engineer, who can collaborate to complete software development tasks.

### 1.3 Execution

Run the `software_team` example:

```bash
python main.py -t software_team
```

Enter your requirements in the interactive page to start the process.

## 2. SDK Development

The core protocol part of `AgentMesh` is provided through an SDK, allowing developers to build a multi-agent team based on this SDK.

Install the SDK dependency:

```bash
pip install agentmesh
```

Here's a simple usage example:

```python
from agentmesh import AgentTeam, Agent, LLMModel
from agentmesh.tools import *

# model
model = LLMModel(model="gpt-4o", api_key="YOUR_API_KEY")

# team build and add agents
team = AgentTeam(name="software_team", description="A software development team", model=model)

team.add(Agent(name="Developer", description="Implements code based on PRD and architecture design", model=model,
               system_prompt="You are a proficient developer who writes clean, efficient, and maintainable code. Follow the PRD requirements and architecture guidelines precisely",
               tools=[Calculator(), BrowserTool()]))

team.add(Agent(name="PM", description="Responsible for product requirements and documentation", system_prompt="You are an experienced product manager who creates clear and comprehensive PRDs"))

# run user task
team.run(task="Write a Snake client game")
```

## 3. Web Service

Coming soon