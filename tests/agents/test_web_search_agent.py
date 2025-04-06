import pytest
from unittest.mock import patch, MagicMock
from simple_agents.agents.web_search.agent import WebSearchAgent
from simple_agents.planner.llm_planner import LLMPlanner
from simple_agents.agents.web_search.tools import WebSearchTool

@pytest.fixture
def web_search_agent():
    planner = LLMPlanner(
        model="gemma3:4b",
        system_prompt="""You are a web search planner. Your task is to:
1. Analyze the user's query
2. Plan web searches to answer the query
3. Return a JSON plan with search steps

Format your response as JSON with a "steps" array containing search steps.
Each step should have:
- tool_name: "web_search"
- arguments: { "query": "search query" }
"""
    )
    tools = {"web_search": WebSearchTool()}
    return WebSearchAgent(agent_name="WebSearchAgent", tools=tools, planner=planner)

@patch('simple_agents.planner.llm_planner.chat')
def test_web_search_agent_plan(mock_chat, web_search_agent):
    """Test that the agent plans correctly."""
    mock_chat.return_value.message.content = '{"steps": [{"tool_name": "web_search", "arguments": {"query": "test query"}}]}'
    
    web_search_agent.receive_task({"task_type": "websearch", "user_input": "test query"})
    web_search_agent.plan()
    
    assert len(web_search_agent.state["steps"]) == 1
    assert web_search_agent.state["steps"][0]["tool_name"] == "web_search"
    assert web_search_agent.state["steps"][0]["arguments"]["query"] == "test query"

@patch('simple_agents.planner.llm_planner.chat')
@patch('simple_agents.coordinator_assistant.chat')
def test_web_search_agent_run(mock_coordinator_chat, mock_planner_chat, web_search_agent):
    """Test the full run method."""
    # Mock the planning response
    mock_planner_chat.return_value.message.content = '{"steps": [{"tool_name": "web_search", "arguments": {"query": "test query"}}]}'
    # Mock the summarization response
    mock_coordinator_chat.return_value.message.content = "Here's what I found in the search results"
    
    result = web_search_agent.run({"task_type": "websearch", "user_input": "test query"})
    
    assert result["agent"] == "WebSearchAgent"
    assert len(result["results"]) == 1
    assert result["results"][0]["tool"] == "web_search"
    assert "summary" in result
    assert isinstance(result["summary"], str)
    assert len(result["summary"]) > 0  # Ensure we have a non-empty summary

@patch('simple_agents.planner.llm_planner.chat')
@patch('simple_agents.coordinator_assistant.chat')
def test_web_search_agent_empty_results(mock_coordinator_chat, mock_planner_chat, web_search_agent):
    """Test handling of empty search results."""
    # Mock the planning response
    mock_planner_chat.return_value.message.content = '{"steps": [{"tool_name": "web_search", "arguments": {"query": "test query"}}]}'
    # Mock the summarization response
    mock_coordinator_chat.return_value.message.content = "No relevant information found"
    
    result = web_search_agent.run({"task_type": "websearch", "user_input": "test query"})
    
    assert result["agent"] == "WebSearchAgent"
    assert len(result["results"]) == 1
    assert result["results"][0]["tool"] == "web_search"
    assert "summary" in result
    assert isinstance(result["summary"], str)
    assert len(result["summary"]) > 0  # Ensure we have a non-empty summary 