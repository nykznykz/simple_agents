import pytest
from unittest.mock import patch, MagicMock
from simple_agents.agents.greet.agent import GreetUserAgent
from simple_agents.agents.greet.tools import GreetUserTool, ReverseNameTool

def test_greet_agent_initialization(greet_agent):
    """Test that the greet agent initializes correctly."""
    assert greet_agent.agent_name == "GreeterAgent"
    assert "say_hello" in greet_agent.tools
    assert "name_backwards" in greet_agent.tools

@patch('simple_agents.planner.llm_planner.chat')
def test_greet_agent_plan(mock_chat, greet_agent):
    """Test that the agent can plan tool execution."""
    mock_chat.return_value.message.content = '''
    {
      "steps": [
        {
          "tool_name": "say_hello",
          "arguments": {
            "name": "Alice"
          }
        }
      ]
    }
    '''
    
    task = {"user_input": "Hello Alice"}
    greet_agent.task = task
    greet_agent.plan()
    assert greet_agent.state["steps"][0]["tool_name"] == "say_hello"
    assert greet_agent.state["steps"][0]["arguments"]["name"] == "Alice"

@patch('simple_agents.planner.llm_planner.chat')
def test_greet_agent_run(mock_chat, greet_agent):
    """Test the full run method of the greet agent."""
    mock_chat.return_value.message.content = '''
    {
      "steps": [
        {
          "tool_name": "say_hello",
          "arguments": {
            "name": "Alice"
          }
        }
      ]
    }
    '''
    
    task = {"user_input": "Hello Alice"}
    result = greet_agent.run(task)
    assert "greeting" in result["results"][0]["output"]

@patch('simple_agents.planner.llm_planner.chat')
def test_greet_agent_multiple_steps(mock_chat, greet_agent):
    """Test that the agent can handle multiple tool steps."""
    mock_chat.return_value.message.content = '''
    {
      "steps": [
        {
          "tool_name": "say_hello",
          "arguments": {
            "name": "Alice"
          }
        },
        {
          "tool_name": "name_backwards",
          "arguments": {
            "name": "Alice"
          }
        }
      ]
    }
    '''
    
    task = {"user_input": "Hello Alice and reverse my name"}
    result = greet_agent.run(task)
    assert "greeting" in result["results"][0]["output"]
    assert "reversed_name" in result["results"][1]["output"] 