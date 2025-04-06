from ...base.base_agent import BaseAgent
from ...base.validation import validate_tool_plan
from ...planner.llm_planner import LLMPlanner
from ...coordinator_assistant import chat



class WebSearchAgent(BaseAgent):
    def __init__(self, agent_name: str, tools: dict, planner: LLMPlanner, model: str = "gemma3:4b"):
        super().__init__(agent_name=agent_name, tools=tools, planner=planner)
        self.model_name = model
        self.system_prompt = """You are a web search specialist agent. Your task is to:
1. Plan and execute web searches to answer user queries
2. Analyze and summarize the search results
3. Provide clear, concise answers based on the search results

When summarizing results:
- Focus on the most relevant information
- Be specific and accurate
- Include key details from the search results
- Format the response in a natural, conversational way
- If the results are unclear or conflicting, acknowledge this
- If no relevant information is found, say so clearly

Available tools:
- web_search: Search the web for information. Takes a 'query' parameter.
"""

    def plan(self):
        user_input = self.task.get("user_input")
        plan = self.planner.plan(user_input)
        validate_tool_plan(plan)
        self.state["steps"] = plan["steps"]
        self.logger.info(f"{self.agent_name} planned steps: {plan['steps']}")

    def _summarize_results(self, results):
        """Summarize the search results using the LLM."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""Please summarize these search results to answer the user's query:

Search Results:
{results}

Provide a clear, concise summary that directly answers the user's question."""}
        ]
        
        response = chat(self.model_name, messages)
        return response.message.content

    def execute(self):
        results = []
        for step in self.state["steps"]:
            tool_name = step.get("tool_name")
            arguments = step.get("arguments", {})

            if tool_name not in self.tools:
                raise ValueError(f"Tool '{tool_name}' not found.")

            self.logger.info(f"{self.agent_name} executing {tool_name} with arguments: {arguments}")
            output = self.tools[tool_name].run(arguments)
            results.append({
                "tool": tool_name,
                "input": arguments,
                "output": output
            })

        # Summarize the results
        summary = self._summarize_results(results)
        
        result = {
            "agent": self.agent_name,
            "results": results,
            "summary": summary
        }
        self.logger.info(f"{self.agent_name} completed execution with results: {result}")
        return result