from ...base.base_tool import BaseTool

class GreetUserTool(BaseTool):
    def run(self, input_data: dict) -> dict:
        name = input_data.get("name", "")
        if not name:
            return {"greeting": "Hello there!"}
        return {"greeting": f"Hello {name}!"}

class ReverseNameTool(BaseTool):
    def run(self, input_data: dict) -> dict:
        name = input_data.get("name", "")
        return {"reversed_name": name[::-1]}
