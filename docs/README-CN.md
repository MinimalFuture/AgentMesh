<p align="center"><img src= "https://github.com/user-attachments/assets/743bb0da-3070-4e89-b744-e7b3ab886fe8" alt="AgentMesh" width="450" /></p>


<a href="/README.md">English</a> | 中文

AgentMesh是一个开源的 **多智能体 (Multi-agent) 平台** ，提供开箱即用的Agent开发框架、多Agent间的协同策略、任务规划和自主决策能力。
在该平台上可以快速构建你的Agent团队，通过多Agent之间的协同完成任务。

# 概述

AgentMesh 采用模块化分层设计，提供灵活且可扩展的多智能体系统构建能力：

- 多Agent协同：支持多Agent角色定义、任务分配、多轮自主决策，即将支持与远程异构Agent的通信协议
- 多模态模型：支持 OpenAI、Claude、DeepSeek 等主流大语言模型，统一接口设计支持无缝切换
- 可扩展工具：内置搜索引擎、浏览器、文件系统、终端等工具，并将通过支持 MCP 协议获得更多工具扩展
- 多端运行：支持命令行、Docker、SDK 等多种运行方式，即将支持 WebUI 及多种常用软件的集成

# 快速开始

提供三种使用方式快速构建并运行你的 Agent Team：

## 一、终端运行

在终端中命令行中快速运行多智能体团队:

### 1.安装

**环境准备：** 支持 Linux、MacOS、Windows 系统，需要安装 python。

> python 版本推荐使用 3.11+ (如需使用浏览器工具)，至少需要 3.7
> 以上。下载地址：[python官网](https://www.python.org/downloads/)。

下载项目源码并进入项目目录：

```bash
git clone https://github.com/MinimalFuture/AgentMesh
cd AgentMesh
```

核心依赖安装：

```bash
pip install -r requirements.txt
```

如需使用浏览器工具，还需要额外安装依赖 (可选，需要 python3.11+):

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

# 详细介绍

## 概念

- Agent: 智能体，具有特定角色和能力的自主决策单元，可配置模型、系统提示词、工具集和决策逻辑
- AgentTeam: 智能体团队，由多个Agent组成，负责任务分配、上下文管理和协作流程控制
- Tool: 工具，扩展Agent能力的功能模块，如计算器、搜索引擎、浏览器等
- Task: 任务，用户输入的问题或需求，可包含文本、图像等多模态内容
- Context: 上下文，包含团队信息、任务内容和Agent间共享的执行历史
- LLMModel: 大语言模型，支持多种主流大语言模型，统一接口设计

## 模型

- OpenAI: 支持 GPT 系列模型，推荐使用 `gpt-4.1`, `gpt-4o`, `gpt-4.1-mini`
- Claude: 支持 Claude系列模型，推荐使用 `claude-3-7-sonnect-latest`
- DeepSeek: 支持 DeepSeek 系列模型，推荐使用 `deepseek-chat`
- Ollama: 支持本地部署的开源模型 (即将支持)

## 工具

- calculator: 数学计算工具，支持复杂表达式求值
- current_time: 获取当前时间工具，解决模型时间感知问题
- browser: 浏览器操作工具，基于browser-use实现，支持网页访问、内容提取和交互操作
- google_search: 搜索引擎工具，获取最新信息和知识
- MCP: 多模态内容处理工具，支持图像识别和生成（即将支持）

# 贡献

Star支持和关注本项目，可以接受最新的项目更新通知。

欢迎 [提交PR](https://github.com/MinimalFuture/AgentMesh/pulls)
来共同参与这个项目，遇到问题或有任何想法可 [提交Issues](https://github.com/MinimalFuture/AgentMesh/issues) 进行反馈。
