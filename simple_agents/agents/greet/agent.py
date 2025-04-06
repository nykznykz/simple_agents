from ...base.base_agent import BaseAgent
from ...base.validation import validate_tool_plan
from ...coordinator_assistant import chat
from ...planner.llm_planner import LLMPlanner

class GreetUserAgent(BaseAgent):
    def __init__(self, agent_name: str, tools: dict, planner: LLMPlanner, model: str = "gemma3:4b"):
        super().__init__(agent_name=agent_name, tools=tools, planner=planner)
        self.model_name = model
        self.system_prompt = """You are a greeting specialist agent. Your task is to:
1. Generate friendly greetings for users
2. Personalize greetings based on user input
3. Return natural, conversational responses

When generating greetings:
- Be warm and friendly
- Use the user's name if provided
- Keep the response concise but personal
- Format the response in a natural, conversational way
"""

    def plan(self):
        user_input = self.task.get("user_input")
        plan = self.planner.plan(user_input)
        validate_tool_plan(plan)
        self.state["steps"] = plan["steps"]

    def _summarize_results(self, results):
        """Summarize the greeting results using the LLM."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""Please generate a friendly greeting based on these results:

Results:
{results}

Provide a natural, conversational greeting."""}
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
            output = self.tools[tool_name].run(arguments)
            results.append({
                "tool": tool_name,
                "input": arguments,
                "output": output
            })
        
        # Summarize the results
        summary = self._summarize_results(results)
        
        return {
            "agent": self.agent_name,
            "results": results,
            "summary": summary
        }