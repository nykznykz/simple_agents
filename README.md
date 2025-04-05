# 🕵️‍♂️ Simple Agents
A modular, LLM-powered multi-agent framework for interacting with users, invoking tools, and returning natural responses — all orchestrated through a Coordinator Assistant.

# 🧠 Overview
This project is built around the concept of autonomous agents that:

1. Receive tasks from a Coordinator Agent

2. Use an LLM planner to decide which tools to call

3. Execute tools in sequence

4. Return structured outputs

5. The Coordinator routes user input to the right agent and uses another LLM to produce a final conversational reply.

# 🧩 Project Structure
```
simple_agents/
│
├── coordinator_assistant.py   # Main assistant logic
├── main.py                    # CLI runner
│
├── base/                      # Core abstractions
│   ├── base_agent.py
│   ├── base_tool.py
│   └── validation.py
│
├── planner/
│   └── llm_planner.py         # LLM planner for agents
│
├── agents/
│   ├── greet/
│   │   ├── agent.py
│   │   └── tools.py
│   └── ... (your agents here)
│
└── utils/
    └── json_utils.py
```
    
# 🛠 Adding a New Tool
Create (or modify) an agent module inside agents/<agent_name>/tools.py.

Inherit from BaseTool (optional but encouraged).

Implement the run(input_data: dict) -> dict method.

Example:

```python

class UppercaseNameTool(BaseTool):
    def run(self, input_data: dict) -> dict:
        name = input_data.get("name", "")
        return {"uppercased_name": name.upper()}
```

Register it in the tools dict when instantiating the agent:

```python
tools = {
    "uppercase_name": UppercaseNameTool(),
    ...
}
```

Update the agent's system_prompt with the new tool so the LLM knows it exists.

# 🧠 Adding a New Agent
Create a new folder in agents/, e.g. agents/weather/.

Inside it, create:

* agent.py: Subclass BaseAgent

* tools.py: Define your custom tools

Implement the plan() and execute() methods in your agent.

Use LLMPlanner to break user input into tool steps.

Add the agent to the AGENT_REGISTRY in coordinator_assistant.py.

Example:

```python

from agents.weather.agent import WeatherAgent
AGENT_REGISTRY = {
    "greet": GreetUserAgent(...),
    "detect_scam": WeatherAgent(...)
}
```
Update the router prompt in coordinator_assistant.py to include the new agent’s name and purpose.

# 🚀 Running It
From project root:

```bash
python main.py
```
Or in a notebook:

```python
from coordinator_assistant import CoordinatorAssistant

assistant = CoordinatorAssistant()
response = assistant.run("Greet my friend Alice and reverse her name")
print(response)
```
# 💡 Future Ideas
* Add memory to agents

* Enable tool-to-tool state sharing

* Build out an async tool executor

* Expose via API (FastAPI / Flask)

