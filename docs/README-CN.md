<p align="center"><img src= "https://github.com/user-attachments/assets/1499f725-0a7c-42cd-9968-a607a95af5d4" alt="Chatgpt-on-Wechat" width="450" /></p>


<a href="/README.md">English</a> | 中文

AgentMesh是一个 **多智能体 (Multi-agent) 平台** ，提供AI Agent开发框架、多Agent间的通信协议、复杂任务规划和自主决策。 基于该平台可以快速构建你的Agent Team，通过Agents之间的协作完成任务。

# 快速开始

提供三种使用方式快速构建并运行你的 Agent Team：

## 一、终端运行

在终端中命令行中快速运行多智能体团队:

### 1.安装

下载项目源码并进入项目目录：

```bash
git clone https://github.com/MinimalFuture/AgentMesh
cd AgentMesh
```

安装python，要求python3.7以上，推荐使用python3.11+ (使用浏览器工具依赖python 3.11以上)。

推荐使用python虚拟环境工具uv一键安装及运行，首先下载uv：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

创建虚拟环境：

```bahs
uv venv --python 3.11
source .venv/bin/activate
```

安装依赖：

```bash
pip install requirements.txt
```

如果需要使用浏览器工具，还需要安装 (可选):

```bash
pip install browser-use
playwright install
```


### 2.配置

配置文件为根目录下的 `config.yaml`，包含模型配置和Agent配置，可以从模板文件复制后修改：

```bash
cp config-template.yaml config.yaml
```

填写需要用到的模型 `api_key`，支持 `openai`、`claude`、`deepseek` 等模型。

配置模板中预置了一个名为 `software_team` 的Agent开发团队，包含产品经理、架构师、工程师三种角色，可以协作完成软件开发任务。

### 3.运行

运行 `software_team` 示例：

```bash
python main.py -t software_team
```

进入交互页面后输入需求内容即可开始运行。


## 二、 SDK开发

`Agentmesh`的核心协议部分通过SDK提供，开发者可基于该SDK构建一个多智能体团队。

安装SDK依赖:

```bash
pip install agentmesh
```

以下是一个简单的使用示例：

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

team.add(Agent(name="PM", description="Responsible for product requirements and documentation", system_prompt="You are an experienced product manager who creates clear and comprehensive PRDs")

# run user task
team.run(task="Write a Snake client game")
```


## 三、Web服务运行

即将支持
