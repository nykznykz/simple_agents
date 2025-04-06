import pytest
from simple_agents.coordinator_assistant import CoordinatorAssistant
from simple_agents.agents.greet.agent import GreetUserAgent
from simple_agents.agents.greet.tools import GreetUserTool, ReverseNameTool
from simple_agents.planner.llm_planner import LLMPlanner

@pytest.fixture
def mock_model():
    """Mock the LLM model for testing."""
    return "gemma3:4b"

@pytest.fixture
def coordinator(mock_model):
    """Create a CoordinatorAssistant instance for testing."""
    return CoordinatorAssistant(model=mock_model)

@pytest.fixture
def greet_agent(mock_model):
    """Create a GreetUserAgent instance for testing."""
    return GreetUserAgent(
        agent_name="GreeterAgent",
        tools={
            "say_hello": GreetUserTool(),
            "name_backwards": ReverseNameTool()
        },
        planner=LLMPlanner(model=mock_model, system_prompt="")
    ) 