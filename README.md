# 🕵️‍♂️ Simple Agents
A modular, LLM-powered multi-agent framework for interacting with users, invoking tools, and returning natural responses — all orchestrated through a Coordinator Assistant.

# 🧠 Overview
This project is built around the concept of autonomous agents that:

1. Receive tasks from a Coordinator Agent
2. Use an LLM planner to decide which tools to call
3. Execute tools in sequence
4. Return structured outputs including a suggested summary
5. The Coordinator routes user input to the right agent(s) and uses another LLM to produce a final conversational reply, using the agent's summary as a suggestion.

Key Features:
- **Multi-Agent Coordination**: Handle complex queries requiring multiple agents
- **Context Sharing**: Agents can access and build upon previous results
- **Message History**: Maintain context across multiple interactions
- **Natural Responses**: Combine multiple agent outputs into coherent responses

# 📊 Example Interaction
Here's a real example showing how the system processes a complex query requiring multiple agents:

```log
# User asks about Bitcoin price and name reversal
2025-04-09 22:14:04,021 - INFO - User Query: What is the price of bitcoin? btw my name is John, I would like to know my name backwards

# Coordinator routes the query to multiple agents
2025-04-09 22:14:04,021 - INFO - Routing decision: [
  {
    "agent": "greet",
    "task": "Greet the user by name and perform name reversal",
    "context": {
      "relevant_info": "User's name is John",
      "user_intent": "Request greeting and name reversal",
      "required_tools": ["say_hello(name: string)", "name_backwards(name: string)"]
    }
  },
  {
    "agent": "websearch",
    "task": "Retrieve the current price of Bitcoin",
    "context": {
      "relevant_info": "User is asking about Bitcoin price",
      "user_intent": "Find the current price of Bitcoin",
      "required_tools": ["web_search(query: string)"]
    }
  }
]

# Coordinator formats a natural response using the agent's summary as a suggestion
2025-04-06 16:49:19,293 - INFO - Final Response: Okay, great question! As of today, April 4th, 2025, 
around 7:31 pm EDT, Bitcoin is trading at $83,674.78 USD. It's up about 1.25% in the last 24 hours, 
and it's the most popular cryptocurrency with a market cap of $1.66 trillion.
```

This example shows:
1. How the coordinator routes queries to multiple appropriate agents
2. How agents plan and execute their tasks in parallel
3. How context is shared between agents
4. How the coordinator combines multiple results into a natural response
5. The structured format of agent results and context sharing

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

# 🧠 Adding a New Agent
Here's an example of adding a new agent to handle mathematical calculations:

1. Create a new directory and files:
```bash
mkdir -p simple_agents/agents/math
touch simple_agents/agents/math/agent.py
touch simple_agents/agents/math/tools.py
```

2. Implement the tools in `tools.py`:
```python
from simple_agents.base.base_tool import BaseTool

class CalculateTool(BaseTool):
    def run(self, input_data: dict) -> dict:
        expression = input_data.get("expression")
        try:
            result = eval(expression)  # Note: In production, use a safer evaluation method
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}

class ConvertUnitsTool(BaseTool):
    def run(self, input_data: dict) -> dict:
        value = input_data.get("value")
        from_unit = input_data.get("from_unit")
        to_unit = input_data.get("to_unit")
        # Implement unit conversion logic
        return {"result": converted_value}
```

3. Implement the agent in `agent.py`:
```python
from simple_agents.base.base_agent import BaseAgent
from simple_agents.planner.llm_planner import LLMPlanner
from .tools import CalculateTool, ConvertUnitsTool

class MathAgent(BaseAgent):
    def __init__(self, model: str):
        system_prompt = """
        You are a math assistant that helps with calculations and unit conversions.
        Available tools:
        1. calculate(expression: string) - Evaluates a mathematical expression
        2. convert_units(value: number, from_unit: string, to_unit: string) - Converts between units
        
        Respond with a JSON array of steps to execute.
        """
        
        tools = {
            "calculate": CalculateTool(),
            "convert_units": ConvertUnitsTool()
        }
        
        planner = LLMPlanner(model=model, system_prompt=system_prompt)
        super().__init__("MathAgent", tools, planner)

    def run(self, task: dict) -> dict:
        result = super().run(task)
        # Add a natural language summary of the calculation
        result["summary"] = f"The result is {result['results'][0]['output']['result']}"
        return result
```

4. Add the agent to the CoordinatorAssistant in `coordinator_assistant.py`:
```python
from simple_agents.agents.math.agent import MathAgent

def _init_agents(self):
    return {
        "greet": build_greet_agent(self.model),
        "websearch": build_web_search_agent(self.model),
        "math": MathAgent(self.model)  # Add the new agent
    }
```

5. Update the routing prompt in `coordinator_assistant.py` to include the new agent:
```python
ROUTER_PROMPT = """
You are a smart routing agent. Given a user message, decide which agents should handle it.

Available agents:
1. greet - for greetings and name-based interactions
2. websearch - to get real time information from the internet
3. math - to perform calculations and unit conversions
...
"""
```

Now the coordinator can route mathematical queries to the new agent:
```python
# Example usage
coordinator = CoordinatorAssistant()
response = coordinator.run([{"role": "user", "content": "What is 2 + 2?"}])
```

# 🎯 Message Format
The system uses a structured message format to maintain context and share information between agents:

```python
{
    "task_type": "agent_name",
    "user_input": "current user message",
    "message_history": [
        {"role": "user", "content": "previous message 1"},
        {"role": "assistant", "content": "previous response 1"}
    ],
    "task": "specific task description",
    "context": {
        "relevant_info": "extracted relevant information",
        "user_intent": "user's intent",
        "required_tools": ["tool1", "tool2"]
    },
    "previous_results": [
        {
            "agent": "previous_agent",
            "results": [...],
            "summary": "previous result summary"
        }
    ]
}
```

# 🎯 Available Agents

## Greet Agent
- **Purpose**: Handles greetings and name-based interactions
- **Tools**:
  - `say_hello(name)`: Greets the user by name
  - `name_backwards(name)`: Reverses the user's name
- **Use Cases**: Greetings, name manipulations, personal interactions

## Web Search Agent
- **Purpose**: Gets real-time information from the internet
- **Tools**:
  - `web_search(query)`: Performs web searches and returns summaries
- **Use Cases**: Current events, factual information, real-time data

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

