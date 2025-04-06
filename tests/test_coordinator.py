import pytest
from unittest.mock import patch, MagicMock

def test_coordinator_initialization(coordinator):
    """Test that the coordinator initializes correctly."""
    assert coordinator.model == "gemma3:4b"
    assert "greet" in coordinator.agents
    assert "websearch" in coordinator.agents

@patch('simple_agents.coordinator_assistant.chat')
def test_route_to_greet_agent(mock_chat, coordinator):
    """Test that the coordinator routes greeting requests correctly."""
    mock_chat.return_value.message.content = '{"agent": "greet"}'
    
    result = coordinator.route("Hello, my name is Alice")
    assert result == "greet"

@patch('simple_agents.coordinator_assistant.chat')
def test_route_to_websearch_agent(mock_chat, coordinator):
    """Test that the coordinator routes search requests correctly."""
    mock_chat.return_value.message.content = '{"agent": "websearch"}'
    
    result = coordinator.route("What is the weather today?")
    assert result == "websearch"

@patch('simple_agents.coordinator_assistant.chat')
def test_route_unknown_agent(mock_chat, coordinator):
    """Test that the coordinator handles unknown agent requests."""
    mock_chat.return_value.message.content = '{"agent": "unknown"}'
    
    result = coordinator.route("Some random request")
    assert result == "unknown"

@patch('simple_agents.coordinator_assistant.chat')
def test_run_with_greet_agent(mock_chat, coordinator):
    """Test the full run method with a greet agent."""
    # Mock the routing and formatting responses
    mock_chat.side_effect = [
        MagicMock(message=MagicMock(content='{"agent": "greet"}')),  # For routing
        MagicMock(message=MagicMock(content='Hello Alice! I am your friendly AI assistant. Nice to meet you!'))  # For formatting
    ]
    
    # Mock the agent's run method
    coordinator.agents["greet"].run = MagicMock(return_value={
        "agent": "GreeterAgent",
        "results": [
            {
                "tool": "say_hello",
                "input": {"name": "Alice"},
                "output": {"greeting": "Hello Alice!"}
            }
        ],
        "summary": "Hello Alice! Nice to meet you!"  # This is now just a suggestion for the coordinator
    })
    
    response = coordinator.run("Hello, my name is Alice")
    assert isinstance(response, str)
    assert "Hello" in response and "Alice" in response
    assert mock_chat.call_count == 2  # Called once for routing and once for formatting 