import logging

class BaseAgent:
    def __init__(self, agent_name, tools=None, planner=None):
        self.agent_name = agent_name
        self.tools = tools or {}
        self.planner = planner
        self.state = {}
        self.messages = {}  # Dictionary to store latest messages by type
        self.logger = logging.getLogger()

    def receive_task(self, task: dict):
        self.task = task
        self.state = {"status": "received", "task_type": task.get("task_type")}
        # Store the latest task received message
        self.messages["task_received"] = str(task)
        self.logger.info(f"{self.agent_name} received task: {task}")

    def plan(self):
        raise NotImplementedError("Subclasses must implement plan()")

    def execute(self):
        raise NotImplementedError("Subclasses must implement execute()")

    def run(self, task: dict):
        self.receive_task(task)
        self.plan()
        result = self.execute()
        # Store the latest result message
        self.messages["result"] = str(result)
        return result
