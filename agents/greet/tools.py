from base.base_tool import BaseTool

class GreetUserTool(BaseTool):
    def run(self, input_data: dict) -> dict:
        name = input_data.get("name", "Anonymous")
        greeting = f"Hello, {name}!"
        print(greeting)
        return {"greeting": greeting}

class ReverseNameTool(BaseTool):
    def run(self, input_data: dict) -> dict:
        name = input_data.get("name", "Anonymous")
        reversed_name = name[::-1]
        print(reversed_name)
        return {"reversename": reversed_name}
