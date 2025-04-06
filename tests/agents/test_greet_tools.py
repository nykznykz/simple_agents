import pytest
from simple_agents.agents.greet.tools import GreetUserTool, ReverseNameTool

def test_greet_user_tool():
    """Test the GreetUserTool functionality."""
    tool = GreetUserTool()
    result = tool.run({"name": "Alice"})
    assert "greeting" in result
    assert "Alice" in result["greeting"]

def test_reverse_name_tool():
    """Test the ReverseNameTool functionality."""
    tool = ReverseNameTool()
    result = tool.run({"name": "Alice"})
    assert "reversed_name" in result
    assert result["reversed_name"] == "ecilA"

def test_greet_user_tool_empty_name():
    """Test GreetUserTool with empty name."""
    tool = GreetUserTool()
    result = tool.run({"name": ""})
    assert "greeting" in result
    assert "there" in result["greeting"].lower()

def test_reverse_name_tool_empty_name():
    """Test ReverseNameTool with empty name."""
    tool = ReverseNameTool()
    result = tool.run({"name": ""})
    assert "reversed_name" in result
    assert result["reversed_name"] == ""

def test_greet_user_tool_special_characters():
    """Test GreetUserTool with special characters in name."""
    tool = GreetUserTool()
    result = tool.run({"name": "Alice-123"})
    assert "greeting" in result
    assert "Alice-123" in result["greeting"]

def test_reverse_name_tool_special_characters():
    """Test ReverseNameTool with special characters in name."""
    tool = ReverseNameTool()
    result = tool.run({"name": "Alice-123"})
    assert "reversed_name" in result
    assert result["reversed_name"] == "321-ecilA" 