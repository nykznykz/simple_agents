import pytest
from unittest.mock import patch, MagicMock
from simple_agents.agents.web_search.tools import WebSearchTool

@patch('simple_agents.agents.web_search.tools.DDGS')
def test_web_search_tool_basic_query(mock_ddgs):
    """Test that WebSearchTool performs a basic search correctly."""
    # Mock the DuckDuckGo search results
    mock_ddgs.return_value.__enter__.return_value.text.return_value = [
        {"body": "First search result"},
        {"body": "Second search result"},
        {"body": "Third search result"}
    ]
    
    tool = WebSearchTool()
    result = tool.run({"query": "test query"})
    
    assert "results" in result
    assert len(result["results"]) == 3
    assert result["results"][0] == "First search result"
    assert result["results"][1] == "Second search result"
    assert result["results"][2] == "Third search result"

@patch('simple_agents.agents.web_search.tools.DDGS')
def test_web_search_tool_empty_query(mock_ddgs):
    """Test that WebSearchTool handles empty queries."""
    # Mock empty search results
    mock_ddgs.return_value.__enter__.return_value.text.return_value = []
    
    tool = WebSearchTool()
    result = tool.run({"query": ""})
    
    assert "results" in result
    assert len(result["results"]) == 0

@patch('simple_agents.agents.web_search.tools.DDGS')
def test_web_search_tool_missing_query(mock_ddgs):
    """Test that WebSearchTool handles missing query parameter."""
    # Mock empty search results
    mock_ddgs.return_value.__enter__.return_value.text.return_value = []
    
    tool = WebSearchTool()
    result = tool.run({})
    
    assert "results" in result
    assert len(result["results"]) == 0

@patch('simple_agents.agents.web_search.tools.DDGS')
def test_web_search_tool_max_results(mock_ddgs):
    """Test that WebSearchTool respects max_results parameter."""
    # Mock the DuckDuckGo search results
    mock_ddgs.return_value.__enter__.return_value.text = lambda query, max_results: [
        {"body": f"Result {i}"} for i in range(min(max_results, 5))
    ]
    
    tool = WebSearchTool()
    result = tool.run({"query": "test query"})
    
    assert "results" in result
    assert len(result["results"]) == 3  # Should be capped at 3 as per the tool implementation 