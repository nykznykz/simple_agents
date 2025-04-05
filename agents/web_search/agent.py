from base.base_agent import BaseAgent
from base.validation import validate_tool_plan



class WebSearchAgent(BaseAgent):
    def plan(self):
        user_input = self.task.get("user_input")
        plan = self.planner.plan(user_input)
        validate_tool_plan(plan)
        self.state["steps"] = plan["steps"]

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

        return {
            "agent": self.agent_name,
            "results": results
        }