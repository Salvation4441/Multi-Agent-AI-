# Multi-Agent-AI-
Multi-Agent AI customer support system with LIVE Streaming, Python, Django, Claude API, RAG, ChromaDB, and LangChain

## AI AGENT
 - An AI agent is a system that can preceive its environment,make decisions,take actions, and work towards a common goal autonomously

    * Perceive  : its reads the situation
    * Act : it calls tools,queries data
    * Decide : it figures out next steps
    * Repeat : it repeat until the goal is reached

## Agentic AI
It is an intelligent systems that operate autonomously to achieve goals with minimal human supervision


## Tool
This is just a regular python function that does something useful

## Agent Loop
The things keeps the agent going,keeps looping is  called the Agent Loop

 - Think ---> Act ---> Check ---> Repeat

The agent decides if it has enough information. If not, it uses a tool,gets a result, and think again. 
Once satisfied,it delivers the *Final result*

 The Loop exits only when the agent has enough informations to answer


## Agent Frameworks
 - This are python libraries for building AI agents.

 - Pre-built components,agents classes and tool integrations,so you do not build them from scratch

    - Pre-built Components : Read-made building blocks for common agent task
    - Agent Classes : Structured abstractions for defining agent behavior.
    - Tool Integrations: Connect to APIs,databases and external services instantly

1. LANGCHAIN
The most widely used framework for building AI agents. It use to create agents,chains and tool integrations  with  minimal code.

    - Chain: It does multiple things in specific order, one after another

    - Agents: It is an autonomously  decision-making tool access built in.

    - Integrations : Hundreds of ready-made connectors for tools and data sources

2. AUTOGEN
This is a multiple agent with roles and it collaborate automatically. AutoGen orchestrates the conversation between agents so that complex task get solved through team work.

    - Define Agents : Assign each agent a name,role, and system propmt.

    - Set the Task : Give the group a goal or problem to solve together.

    - Collaborate : Agents message each other automatically until the task is complete.

3. CREW AI (Team of Agent)
Assign roles,goals and task to each agent, Crew AI handles the teamwork. Think of it as building a crew where every member knows their job assigned.
    
    - Roles : Each agent gets a specific identity and area of expertise.

    - Goals : Agents are driven by individual objectives that serves the crew.

    - Task : Discrete unit of work assigned and tracked automatically.


<!-- pip freeze  >  requirements.txt   (To install all libraries) -->
<!-- pip install -r requirements.txt   (To install all libraries) -->