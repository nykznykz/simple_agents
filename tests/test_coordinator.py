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
    mock_chat.return_value.message.content = '{"agents": [{"agent": "greet", "task": "Greet the user", "context": {"relevant_info": "User name is Alice", "user_intent": "wants to be greeted", "required_tools": ["say_hello"]}}]}'
    
    result = coordinator.route("Hello, my name is Alice")
    assert len(result) == 1
    assert result[0]["agent"] == "greet"
    assert result[0]["task"] == "Greet the user"
    assert result[0]["context"]["relevant_info"] == "User name is Alice"
    assert result[0]["context"]["user_intent"] == "wants to be greeted"
    assert "say_hello" in result[0]["context"]["required_tools"]

@patch('simple_agents.coordinator_assistant.chat')
def test_route_to_websearch_agent(mock_chat, coordinator):
    """Test that the coordinator routes search requests correctly."""
    mock_chat.return_value.message.content = '{"agents": [{"agent": "websearch", "task": "Search for weather information", "context": {"relevant_info": "User wants current weather", "user_intent": "get weather update", "required_tools": ["web_search"]}}]}'
    
    result = coordinator.route("What is the weather today?")
    assert len(result) == 1
    assert result[0]["agent"] == "websearch"
    assert result[0]["task"] == "Search for weather information"
    assert result[0]["context"]["relevant_info"] == "User wants current weather"
    assert result[0]["context"]["user_intent"] == "get weather update"
    assert "web_search" in result[0]["context"]["required_tools"]

@patch('simple_agents.coordinator_assistant.chat')
def test_route_multiple_agents(mock_chat, coordinator):
    """Test that the coordinator can route to multiple agents."""
    mock_chat.return_value.message.content = '{"agents": [{"agent": "greet", "task": "Greet the user", "context": {"relevant_info": "User name is Alice", "user_intent": "wants to be greeted", "required_tools": ["say_hello"]}}, {"agent": "websearch", "task": "Search for weather information", "context": {"relevant_info": "User wants current weather", "user_intent": "get weather update", "required_tools": ["web_search"]}}]}'
    
    result = coordinator.route("Hi, I'm Alice. What's the weather like?")
    assert len(result) == 2
    assert result[0]["agent"] == "greet"
    assert result[0]["task"] == "Greet the user"
    assert result[0]["context"]["relevant_info"] == "User name is Alice"
    assert "say_hello" in result[0]["context"]["required_tools"]
    assert result[1]["agent"] == "websearch"
    assert result[1]["task"] == "Search for weather information"
    assert result[1]["context"]["relevant_info"] == "User wants current weather"
    assert "web_search" in result[1]["context"]["required_tools"]

@patch('simple_agents.coordinator_assistant.chat')
def test_run_with_greet_agent(mock_chat, coordinator):
    """Test the full run method with a greet agent."""
    # Mock the routing and formatting responses
    mock_chat.side_effect = [
        MagicMock(message=MagicMock(content='{"agents": [{"agent": "greet", "task": "Greet the user", "context": {"relevant_info": "User name is Alice", "user_intent": "wants to be greeted", "required_tools": ["say_hello"]}}]}')),  # For routing
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
        "summary": "Hello Alice! Nice to meet you!"
    })
    
    response = coordinator.run("Hello, my name is Alice")
    assert isinstance(response, str)
    assert "Hello" in response and "Alice" in response
    assert mock_chat.call_count == 2  # Called once for routing and once for formatting

@patch('simple_agents.coordinator_assistant.chat')
def test_run_with_multiple_agents(mock_chat, coordinator):
    """Test the full run method with multiple agents."""
    # Mock the routing response
    mock_chat.side_effect = [
        MagicMock(message=MagicMock(content='{"agents": [{"agent": "greet", "task": "Greet the user", "context": {"relevant_info": "User name is Alice", "user_intent": "wants to be greeted", "required_tools": ["say_hello"]}}, {"agent": "websearch", "task": "Search for weather information", "context": {"relevant_info": "User wants current weather", "user_intent": "get weather update", "required_tools": ["web_search"]}}]}')),  # For routing
        MagicMock(message=MagicMock(content='Hello Alice! The weather is sunny today.'))  # For formatting
    ]
    
    # Mock the agents' run methods
    coordinator.agents["greet"].run = MagicMock(return_value={
        "agent": "GreeterAgent",
        "results": [
            {
                "tool": "say_hello",
                "input": {"name": "Alice"},
                "output": {"greeting": "Hello Alice!"}
            }
        ],
        "summary": "Hello Alice! Nice to meet you!"
    })
    
    coordinator.agents["websearch"].run = MagicMock(return_value={
        "agent": "WebSearchAgent",
        "results": [
            {
                "tool": "web_search",
                "input": {"query": "weather today"},
                "output": {"weather": "sunny"}
            }
        ],
        "summary": "The weather is sunny today."
    })
    
    response = coordinator.run("Hi, I'm Alice. What's the weather like?")
    assert isinstance(response, str)
    assert "Hello" in response and "Alice" in response
    assert "weather" in response and "sunny" in response
    assert mock_chat.call_count == 2  # Called once for routing and once for formatting 