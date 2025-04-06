import pytest
from simple_agents.base.validation import validate_tool_plan

def test_validate_tool_plan_valid():
    """Test validation of a valid tool plan."""
    plan = {
        "steps": [
            {
                "tool_name": "test_tool",
                "arguments": {"arg1": "value1"}
            }
        ]
    }
    # Should not raise any exception
    validate_tool_plan(plan)

def test_validate_tool_plan_missing_steps():
    """Test validation fails when steps key is missing."""
    plan = {"not_steps": []}
    with pytest.raises(ValueError, match="Missing 'steps' in plan"):
        validate_tool_plan(plan)

def test_validate_tool_plan_invalid_steps_type():
    """Test validation fails when steps is not a list."""
    plan = {"steps": "not a list"}
    with pytest.raises(ValueError, match="'steps' must be a list"):
        validate_tool_plan(plan)

def test_validate_tool_plan_missing_tool_name():
    """Test validation fails when tool_name is missing."""
    plan = {
        "steps": [
            {
                "arguments": {"arg1": "value1"}
            }
        ]
    }
    with pytest.raises(ValueError, match="Step 0 missing 'tool_name' or 'arguments'"):
        validate_tool_plan(plan)

def test_validate_tool_plan_missing_arguments():
    """Test validation fails when arguments is missing."""
    plan = {
        "steps": [
            {
                "tool_name": "test_tool"
            }
        ]
    }
    with pytest.raises(ValueError, match="Step 0 missing 'tool_name' or 'arguments'"):
        validate_tool_plan(plan)

def test_validate_tool_plan_multiple_steps():
    """Test validation of a plan with multiple steps."""
    plan = {
        "steps": [
            {
                "tool_name": "tool1",
                "arguments": {"arg1": "value1"}
            },
            {
                "tool_name": "tool2",
                "arguments": {"arg2": "value2"}
            }
        ]
    }
    # Should not raise any exception
    validate_tool_plan(plan)

def test_validate_tool_plan_empty_steps():
    """Test validation of a plan with empty steps list."""
    plan = {"steps": []}
    # Should not raise any exception
    validate_tool_plan(plan) 