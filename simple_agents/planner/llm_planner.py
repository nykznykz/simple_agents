from ollama import chat
from ollama import ChatResponse
from ..utils.json_utils import extract_json


class LLMPlanner:
    def __init__(self, model: str, system_prompt: str):
        self.model = model
        self.system_prompt = system_prompt

    def plan(self, user_input: str) -> dict:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input}
        ]
        response = chat(self.model,messages)
        content = response.message.content
        try:
            json_content = extract_json(content)
        except Exception as e:
            raise ValueError(f"Planner failed to parse JSON: {e}\nOutput was: {content}")
        try:
            return json_content
        except Exception as e:
            raise ValueError(f"Planner failed to parse JSON: {e}\nOutput was: {content}")