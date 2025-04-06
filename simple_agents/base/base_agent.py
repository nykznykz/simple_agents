import logging

class BaseAgent:
    def __init__(self, agent_name, tools=None, planner=None):
        self.agent_name = agent_name
        self.tools = tools or {}
        self.planner = planner
        self.state = {}
        self.last_messages = []
        self.logger = logging.getLogger()

    def receive_task(self, task: dict):
        self.task = task
        self.state = {"status": "received", "task_type": task.get("task_type")}
        # Log the received task
        self.last_messages.append(("task_received", str(task)))
        self.logger.info(f"{self.agent_name} received task: {task}")

    def plan(self):
        raise NotImplementedError("Subclasses must implement plan()")

    def execute(self):
        raise NotImplementedError("Subclasses must implement execute()")

    def run(self, task: dict):
        self.receive_task(task)
        self.plan()
        result = self.execute()
        # Log the final result
        self.last_messages.append(("result", str(result)))
        self.logger.info(f"{self.agent_name} produced result: {result}")
        return result
