import json
from ollama import chat

from agents.greet.agent import GreetUserAgent
from agents.greet.tools import GreetUserTool, ReverseNameTool

from agents.web_search.agent import WebSearchAgent
from agents.web_search.tools import WebSearchTool


from planner.llm_planner import LLMPlanner
from utils.json_utils import extract_json

MODEL = "gemma3:4b"

# --- LLM PROMPTS ---

ROUTER_PROMPT = """
You are a smart routing agent. Given a user message, decide which agent should handle it.

Only respond with the name of the agent as a JSON string. Do not include explanations.

Available agents:
1. greet — for greetings and name-based interactions
2. websearch - to get real time information from the internet

Respond in this format:
{
  "agent": "<agent_name>"
}
"""

FORMATTER_PROMPT = """
You are a helpful assistant. Given the user's original request and the structured output from a specialized agent, summarize the response in a natural, conversational way.

Only respond with the assistant's final reply. Do not include any JSON, tool names, or internal details.

Be friendly, clear, and helpful.
"""



def build_greet_agent(model: str) -> GreetUserAgent:
    greet_prompt = """
    You are an AI assistant that decides which tools to call and in what order based on user input.
    
    Only respond with JSON. Do not include any explanations or markdown.
    
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

    def route(self, user_input: str) -> str:
        messages = [
            {"role": "system", "content": ROUTER_PROMPT},
            {"role": "user", "content": user_input}
        ]
        response = chat(self.model, messages)
        routing = extract_json(response.message.content)
        return routing.get("agent", "unknown")

    # def format_response(self, agent_result: dict, user_input: str) -> str:
    #     content = json.dumps(agent_result, indent=2)
    #     messages = [
    #         {"role": "system", "content": FORMATTER_PROMPT},
    #         {"role": "user", "content": f"User input: {user_input}\n\nAgent result:\n{content}"}
    #     ]
    #     response = chat(self.model, messages)
    #     return response.message.content.strip()
    
    def format_response(self, agent_result: dict, user_input: str) -> str:
        content = json.dumps(agent_result, indent=2)
    
        messages = [
            {"role": "system", "content": FORMATTER_PROMPT},
            {"role": "user", "content": f"Conversation so far:\n{user_input}\n\nAgent result:\n{content}"}
        ]
    
        response = chat(self.model, messages)
        return response.message.content.strip()

    def run(self, user_input: str) -> str:
        agent_name = self.route(user_input)

        if agent_name not in self.agents:
            return f"Sorry, I don't have an agent for that request. (Agent: {agent_name})"

        task = {
            "task_type": agent_name,
            "user_input": user_input
        }

        agent = self.agents[agent_name]
        result = agent.run(task)
        return self.format_response(result, user_input)