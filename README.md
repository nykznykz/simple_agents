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
├── coordinator_assistant.py   # Main coordinator logic
├── main.py                    # Gradio interface
│
├── base/                      # Core abstractions
│   ├── base_agent.py         # Base agent class
│   ├── base_tool.py          # Base tool class
│   └── validation.py         # Validation utilities
│
├── planner/
│   └── llm_planner.py        # LLM planner for agents
│
├── agents/                    # Specialized agents
│   ├── greet/                # Greeting agent
│   │   ├── agent.py         # GreetUserAgent implementation
│   │   └── tools.py         # Greeting tools
│   └── web_search/          # Web search agent
│       ├── agent.py         # WebSearchAgent implementation
│       └── tools.py         # Web search tools
│
└── utils/
    └── json_utils.py        # JSON utilities
```

# 🛠 Adding a New Tool
Create a new tool class in the appropriate agent's tools.py file:

```python
from simple_agents.base.base_tool import BaseTool

class MyCustomTool(BaseTool):
    def run(self, input_data: dict) -> dict:
        # Your tool logic here
        return {"result": "your result"}
```

Register the tool in the agent's initialization:

```python
tools = {
    "my_custom_tool": MyCustomTool(),
    # ... other tools
}
```

Update the agent's system prompt to include the new tool's description.

# 🧠 Adding a New Agent
1. Create a new directory in `agents/` for your agent
2. Create `agent.py` and `tools.py` files
3. Implement your agent by subclassing `BaseAgent`:

```python
from simple_agents.base.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def plan(self):
        # Use self.planner to generate a plan
        pass

    def execute(self):
        # Execute the planned steps
        pass
```

4. Add your agent to the CoordinatorAssistant's initialization:

```python
def _init_agents(self):
    return {
        "my_agent": MyCustomAgent(...),
        # ... other agents
    }
```

5. Update the routing prompt in `coordinator_assistant.py` to include your new agent.

# 🚀 Running the Application
1. Install dependencies:
```bash
pip install -e .
```

2. Run the Gradio interface:
```bash
python -m simple_agents.main
```

The application will start a web interface where you can interact with the agents.

# 📝 Logging
The application logs all interactions to `chat.log`. You can clear the log using:
```bash
./clear_chat_log.sh
```

# 💡 Future Ideas
* Add memory to agents
* Enable tool-to-tool state sharing
* Build out an async tool executor
* Add more specialized agents
* Improve error handling and recovery
* Add support for more LLM providers

