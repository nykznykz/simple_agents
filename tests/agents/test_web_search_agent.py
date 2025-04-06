import pytest
from unittest.mock import patch, MagicMock
from simple_agents.agents.web_search.agent import WebSearchAgent
from simple_agents.agents.web_search.tools import WebSearchTool
from simple_agents.planner.llm_planner import LLMPlanner

@pytest.fixture
def web_search_agent(mock_model):
    """Create a WebSearchAgent instance for testing."""
    return WebSearchAgent(
        agent_name="WebSearchAgent",
        tools={"web_search": WebSearchTool()},
        planner=LLMPlanner(model=mock_model, system_prompt="")
    )

def test_web_search_agent_initialization(web_search_agent):
    """Test that the web search agent initializes correctly."""
    assert web_search_agent.agent_name == "WebSearchAgent"
    assert "web_search" in web_search_agent.tools

@patch('simple_agents.planner.llm_planner.chat')
@patch('simple_agents.agents.web_search.tools.DDGS')
def test_web_search_agent_plan(mock_ddgs, mock_chat, web_search_agent):
    """Test that the agent can plan web search execution."""
    mock_chat.return_value.message.content = '''
    {
      "steps": [
        {
          "tool_name": "web_search",
          "arguments": {
            "query": "What is Python?"
          }
        }
      ]
    }
    '''
    
    task = {"user_input": "What is Python?"}
    web_search_agent.task = task
    web_search_agent.plan()
    assert web_search_agent.state["steps"][0]["tool_name"] == "web_search"
    assert web_search_agent.state["steps"][0]["arguments"]["query"] == "What is Python?"

@patch('simple_agents.planner.llm_planner.chat')
@patch('simple_agents.agents.web_search.tools.DDGS')
def test_web_search_agent_run(mock_ddgs, mock_chat, web_search_agent):
    """Test the full run method of the web search agent."""
    # Mock the planner response
    mock_chat.return_value.message.content = '''
    {
      "steps": [
        {
          "tool_name": "web_search",
          "arguments": {
            "query": "What is Python?"
          }
        }
      ]
    }
    '''
    
    # Mock the search results
    mock_ddgs.return_value.__enter__.return_value.text.return_value = [
        {"body": "Python is a programming language"},
        {"body": "Python was created by Guido van Rossum"},
        {"body": "Python is known for its simplicity"}
    ]
    
    task = {"user_input": "What is Python?"}
    result = web_search_agent.run(task)
    
    assert result["agent"] == "WebSearchAgent"
    assert len(result["results"]) == 1
    assert result["results"][0]["tool"] == "web_search"
    assert len(result["results"][0]["output"]["results"]) == 3
    assert "Python" in result["results"][0]["output"]["results"][0]

@patch('simple_agents.planner.llm_planner.chat')
@patch('simple_agents.agents.web_search.tools.DDGS')
def test_web_search_agent_empty_results(mock_ddgs, mock_chat, web_search_agent):
    """Test that the agent handles empty search results correctly."""
    # Mock the planner response
    mock_chat.return_value.message.content = '''
    {
      "steps": [
        {
          "tool_name": "web_search",
          "arguments": {
            "query": "nonexistent query that returns no results"
          }
        }
      ]
    }
    '''
    
    # Mock empty search results
    mock_ddgs.return_value.__enter__.return_value.text.return_value = []
    
    task = {"user_input": "nonexistent query that returns no results"}
    result = web_search_agent.run(task)
    
    assert result["agent"] == "WebSearchAgent"
    assert len(result["results"]) == 1
    assert result["results"][0]["tool"] == "web_search"
    assert len(result["results"][0]["output"]["results"]) == 0 