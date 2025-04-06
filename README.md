# 🕵️‍♂️ Simple Agents
A modular, LLM-powered multi-agent framework for interacting with users, invoking tools, and returning natural responses — all orchestrated through a Coordinator Assistant.

# 🧠 Overview
This project is built around the concept of autonomous agents that:

1. Receive tasks from a Coordinator Agent
2. Use an LLM planner to decide which tools to call
3. Execute tools in sequence
4. Return structured outputs including a suggested summary
5. The Coordinator routes user input to the right agent and uses another LLM to produce a final conversational reply, using the agent's summary as a suggestion.

# 📊 Example Interaction
Here's a real example from the chat log showing how the system processes a user query about Bitcoin's price:

```log
# User asks about Bitcoin price
2025-04-06 16:49:11,263 - INFO - User Query: What is the current price of Bitcoin in USD?

# Coordinator routes the query to the websearch agent
2025-04-06 16:49:15,135 - INFO - Routing decision: websearch
2025-04-06 16:49:15,136 - INFO - Task sent to websearch: {'task_type': 'websearch', 'user_input': '\nUser: What is the current price of Bitcoin in USD?'}

# WebSearchAgent plans and executes the search
2025-04-06 16:49:15,834 - INFO - WebSearchAgent planned steps: [{'tool_name': 'web_search', 'arguments': {'query': 'bitcoin price usd'}}]
2025-04-06 16:49:15,834 - INFO - Querying DuckDuckGo: bitcoin price usd

# Search results are received and processed
2025-04-06 16:49:16,607 - INFO - Query results: ['The live Bitcoin price today is $83,713.14 USD...', ...]

# Agent returns structured results with a suggested summary
2025-04-06 16:49:18,029 - INFO - WebSearchAgent produced result: {
  "agent": "WebSearchAgent",
  "results": [
    {
      "tool": "web_search",
      "input": {"query": "bitcoin price usd"},
      "output": {
        "results": [
          "The live Bitcoin price today is $83,713.14 USD...",
          "Get the latest Bitcoin (BTC / USD) real-time quote...",
          "The price of Bitcoin (BTC) is $83,674.78 today..."
        ]
      }
    }
  ],
  "summary": "As of today, April 4, 2025, at 7:31 pm EDT, the live Bitcoin (BTC) price is $83,674.78 USD. 
  The 24-hour trading volume is $25.3 billion. Bitcoin is currently up 1.25% in the last 24 hours and 
  holds the #1 ranking on CoinMarketCap with a market cap of $1,661,431,078,832 USD."
}

# Coordinator formats a natural response using the agent's summary as a suggestion
2025-04-06 16:49:19,293 - INFO - Final Response: Okay, great question! As of today, April 4th, 2025, 
around 7:31 pm EDT, Bitcoin is trading at $83,674.78 USD. It's up about 1.25% in the last 24 hours, 
and it's the most popular cryptocurrency with a market cap of $1.66 trillion.
```

This example shows:
1. How the coordinator routes queries to appropriate agents
2. How agents plan and execute their tasks
3. The structured format of agent results, including a suggested summary
4. How the coordinator uses the agent's summary as a suggestion to create a natural response
5. The difference between the agent's detailed summary and the coordinator's more conversational response

# 📝 Project Structure
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

    def run(self, task: dict) -> dict:
        # Override run to include a summary in the result
        result = super().run(task)
        result["summary"] = "Your suggested summary here"
        return result
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

The application will start a local web server. You can access it at:
- Local URL: http://127.0.0.1:7860
- Public URL: A temporary public URL will be provided in the console

# 📝 Logging
The application maintains a chat log in `chat.log`. To clear the log when it exceeds 1MB, run:
```bash
./clear_chat_log.sh
```

# 🧪 Testing
Run the test suite:
```bash
python -m pytest
```

For more detailed test output:
```bash
python -m pytest -v
```

# 💡 Future Ideas
* Add memory to agents
* Enable tool-to-tool state sharing
* Build out an async tool executor
* Add more specialized agents
* Improve error handling and recovery
* Add support for more LLM providers

