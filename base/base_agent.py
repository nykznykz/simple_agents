class BaseAgent:
    def __init__(self, agent_name, tools=None, planner=None):
        self.agent_name = agent_name
        self.tools = tools or {}
        self.planner = planner
        self.state = {}

    def receive_task(self, task: dict):
        self.task = task
        self.state = {"status": "received", "task_type": task.get("task_type")}

    def plan(self):
        raise NotImplementedError("Subclasses must implement plan()")

    def execute(self):
        raise NotImplementedError("Subclasses must implement execute()")

    def run(self, task: dict):
        self.receive_task(task)
        self.plan()
        return self.execute()
