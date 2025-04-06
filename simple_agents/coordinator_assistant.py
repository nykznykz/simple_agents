import json
import logging
from ollama import chat

from .agents.greet.agent import GreetUserAgent
from .agents.greet.tools import GreetUserTool, ReverseNameTool

from .agents.web_search.agent import WebSearchAgent
from .agents.web_search.tools import WebSearchTool

from .planner.llm_planner import LLMPlanner
from .utils.json_utils import extract_json

# Get the root logger
logger = logging.getLogger()

MODEL = "gemma3:4b"

# --- LLM PROMPTS ---

ROUTER_PROMPT = """
You are a smart routing agent. Given a user message, decide which agents should handle it and what specific task each agent should perform.

Available agents and their capabilities:

1. greet — for greetings and name-based interactions
   Available tools:
   - say_hello(name: string) — Greets the user by name
   - name_backwards(name: string) — Reverses the user's name
   Use this agent for:
   - Greetings and introductions
   - Name-based interactions
   - Simple name manipulations

2. websearch - to get real time information from the internet
   Available tools:
   - web_search(query: string) — performs a web search and returns short summaries of the top results
   Use this agent for:
   - Finding current information
   - Answering factual questions
   - Getting real-time updates

For each agent, you should:
1. Identify the specific task they should perform
2. Extract relevant context from the user's message that the agent should know
3. Format the task and context in a clear way

Consider:
- If the user's message contains multiple parts that different agents can handle, assign multiple agents
- If the message is simple and can be handled by one agent, use just one agent
- Be specific in the task description for each agent
- Include any relevant context that the agent might need
- Choose agents based on their available tools and capabilities

Respond in this format:
{
  "agents": [
    {
      "agent": "<agent_name>",
      "task": "<specific_task_description>",
      "context": {
        "relevant_info": "<extracted_relevant_information>",
        "user_intent": "<user's_intent>",
        "required_tools": ["<tool1>", "<tool2>"]  # List of tools this agent should use
      }
    }
  ]
}
"""

FORMATTER_PROMPT = """
You are a helpful assistant. Given the user's original request and the structured outputs from multiple specialized agents, combine and summarize the responses in a natural, conversational way.

Consider:
- Combine information from different agents in a logical way
- Remove any redundancy between agent responses
- Maintain a natural flow in the conversation
- Keep the response concise but informative

Only respond with the assistant's final reply. Do not include any JSON, tool names, or internal details.

Be friendly, clear, and helpful.
"""



def build_greet_agent(model: str) -> GreetUserAgent:
    greet_prompt = """
    You are an AI assistant that decides which tools to call and in what order based on user input.
    
    You will receive messages in this format:
    {
      "task_type": "greet",
      "user_input": "What's my name backwards?",
      "task": "Greet the user and perform a name manipulation",
      "context": {
        "relevant_info": "User name is Alice",
        "user_intent": "wants to be greeted and have name reversed",
        "required_tools": ["say_hello", "name_backwards"]
      },
      "previous_results": []
    }

    Important fields to understand:
    - user_input: The user's original query exactly as they typed it
    - task: The coordinator's interpretation of what needs to be done
    - context.relevant_info: Contains important details about the user
    - context.user_intent: Tells you what the user wants to achieve
    - context.required_tools: Lists which tools you should use
    - previous_results: Contains results from other agents if any
    
    Available tools:
    1. say_hello(name: string) — Greets the user by name.
    2. name_backwards(name: string) — Reverses the user's name.
    
    Respond in this format:
    {
      "steps": [
        {
          "tool_name": "<tool_name>",
          "arguments": {
            "<arg1>": <value1>
          }
        }
      ]
    }
    """

    greet_agent = GreetUserAgent(
        agent_name="GreeterAgent",
        tools={
            "say_hello": GreetUserTool(),
            "name_backwards": ReverseNameTool()
        },
        planner=LLMPlanner(model=model, system_prompt=greet_prompt)
    )
    return greet_agent

def build_web_search_agent(model: str) -> WebSearchAgent:
    system_prompt = """
    You are an AI assistant that decides how to answer a user's question using a web search tool.
    
    You will receive messages in this format:
    {
      "task_type": "websearch",
      "user_input": "What's the weather like today?",
      "task": "Search for current weather information",
      "context": {
        "relevant_info": "User wants current weather",
        "user_intent": "get weather update",
        "required_tools": ["web_search"]
      },
      "previous_results": [
        {
          "agent": "GreeterAgent",
          "results": [...],
          "summary": "Hello Alice!"
        }
      ]
    }

    Important fields to understand:
    - user_input: The user's original query exactly as they typed it
    - task: The coordinator's interpretation of what needs to be done
    - context.relevant_info: Contains important details about what to search for
    - context.user_intent: Tells you what the user wants to achieve
    - context.required_tools: Indicates which tools you should use
    - previous_results: May contain relevant information from other agents
    
    Available tools:
    1. web_search(query: string) — performs a web search and returns short summaries of the top results.
    
    Only respond with JSON, do not include explanations or markdown.
    Format:
    {
      "steps": [
        {
          "tool_name": "web_search",
          "arguments": {
            "query": "<search query>"
          }
        }
      ]
    }
    """

    planner = LLMPlanner(model=model, system_prompt=system_prompt)
    tools = {"web_search": WebSearchTool()}

    return WebSearchAgent(agent_name="WebSearchAgent", tools=tools, planner=planner)


# --- Main Coordinator Class ---

class CoordinatorAssistant:
    def __init__(self, model=MODEL):
        self.model = model
        self.agents = self._init_agents()

    def _init_agents(self):
        greet_agent = build_greet_agent(self.model)
        web_search_agent = build_web_search_agent(self.model)
        return {
            "greet": greet_agent,
            "websearch": web_search_agent
        }

    def route(self, user_input: str) -> list:
        messages = [
            {"role": "system", "content": ROUTER_PROMPT},
            {"role": "user", "content": user_input}
        ]
        response = chat(self.model, messages)
        routing = extract_json(response.message.content)
        agent_assignments = routing.get("agents", [])
        logger.info(f"Routing decision: {agent_assignments}")
        return agent_assignments

    def format_response(self, agent_results: list, user_input: str) -> str:
        """Format multiple agent results into a natural response."""
        # Log the raw results for debugging
        logger.info(f"Agent raw results: {json.dumps(agent_results, indent=2)}")
        
        messages = [
            {"role": "system", "content": FORMATTER_PROMPT},
            {"role": "user", "content": f"""Here is the user's input and the agents' results:

User Input: {user_input}

Agent Results: {json.dumps(agent_results, indent=2)}

Please provide a natural, conversational response that combines all the relevant information from the different agents."""}
        ]
        
        response = chat(self.model, messages)
        return response.message.content

    def run(self, user_input: str) -> str:
        agent_assignments = self.route(user_input)
        
        if not agent_assignments:
            return "I'm not sure how to help with that request. Could you please rephrase?"
        
        results = []
        for agent_assignment in agent_assignments:
            agent_name = agent_assignment["agent"]
            if agent_name not in self.agents:
                logger.warning(f"Unknown agent: {agent_name}")
                continue
            
            task = {
                "task_type": agent_name,
                "user_input": agent_assignment["task"],
                "context": agent_assignment.get("context", {}),  # Pass the extracted context
                "previous_results": results  # Pass previous results as context
            }
            
            agent = self.agents[agent_name]
            logger.info(f"Task sent to {agent_name}: {task}")
            
            try:
                result = agent.run(task)
                results.append(result)
                
                # Log the final result from the agent
                if "result" in agent.messages:
                    logger.info(f"{agent_name} (task_received) -> Coordinator: {agent.messages['task_received']}")
                    logger.info(f"{agent_name} (result) -> Coordinator: {agent.messages['result']}")
            except Exception as e:
                logger.error(f"Error running agent {agent_name}: {str(e)}")
                results.append({"error": f"Error running {agent_name}: {str(e)}"})
        
        if not results:
            return "I encountered an error while processing your request. Please try again."
        
        # Format the combined results
        formatted_response = self.format_response(results, user_input)
        logger.info(f"Final Response: {formatted_response}")
        return formatted_response