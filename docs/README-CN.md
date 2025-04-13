<p align="center"><img src= "https://github.com/user-attachments/assets/743bb0da-3070-4e89-b744-e7b3ab886fe8" alt="AgentMesh" width="450" /></p>


<a href="/README.md">English</a> | 中文

AgentMesh是一个 **多智能体 (Multi-agent) 平台** ，提供AI Agent开发框架、多Agent间的通信协议、复杂任务规划和自主决策。
基于该平台可以快速构建你的Agent Team，通过Agents之间的协作完成任务。

# 快速开始

提供三种使用方式快速构建并运行你的 Agent Team：

## 一、终端运行

在终端中命令行中快速运行多智能体团队:

### 1.安装

**环境准备：** 支持 Linux、MacOS、Windows 系统，需要安装 python。

> python 版本要求 3.7 以上，推荐使用 python3.11+ (如需使用浏览器工具)
> 。下载地址：[python官网](https://www.python.org/downloads/)。

下载项目源码并进入项目目录：

```bash
git clone https://github.com/MinimalFuture/AgentMesh
cd AgentMesh
```

核心依赖安装：

```bash
pip install -r requirements.txt
```

如需使用浏览器工具，还需要额外安装依赖 (可选):

```bash
pip install browser-use
playwright install
```

### 2.配置

配置文件为根目录下的 `config.yaml`，包含模型配置和Agent配置，可以从模板文件复制后修改：

```bash
cp config-template.yaml config.yaml
```

填写需要用到的模型 `api_key`，支持 `openai`、`claude`、`deepseek`、`qwen` 等模型。

配置模板中预置了一个名为 `software_team` 的Agent开发团队，包含产品经理、架构师、工程师三种角色，可以协作完成软件开发任务。

### 3.运行

```bash
python main.py -l                   # 查看可用agent team                 
python main.py -t software_team     # 运行名为 'software_team' 的team
```

进入交互模式后输入需求内容即可开始运行。

## 二、 SDK开发

`Agentmesh`的核心模块通过SDK对外提供，开发者可基于该SDK快速构建智能体及多智能体团队。

安装SDK依赖:

```bash
pip install agentmesh-sdk
```

以下是一个简单的使用示例，使用前请替换 `YOUR_API_KEY` 为你的实际API密钥：

```python
from agentmesh import AgentTeam, Agent, LLMModel
from agentmesh.tools import *

# model
model = LLMModel(model="gpt-4o", api_key="YOUR_API_KEY")

# team build and add agents
team = AgentTeam(name="software_team", description="A software development team", model=model)

team.add(Agent(name="PM", description="Responsible for product requirements and documentation",
               system_prompt="You are an experienced product manager who creates clear and comprehensive PRDs"))

team.add(Agent(name="Developer", description="Implements code based on PRD and architecture design", model=model,
               system_prompt="You are a proficient developer who writes clean, efficient, and maintainable code. Follow the PRD requirements and architecture guidelines precisely",
               tools=[Calculator(), GoogleSearch()]))

# run user task
team.run(task="Write a Snake client game")
```

## 三、Web服务运行

即将支持
