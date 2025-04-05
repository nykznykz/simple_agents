def validate_tool_plan(plan: dict):
    if "steps" not in plan:
        raise ValueError(f"Missing 'steps' in plan: {plan}")
    if not isinstance(plan["steps"], list):
        raise ValueError(f"'steps' must be a list: {plan}")

    for i, step in enumerate(plan["steps"]):
        if not all(k in step for k in ("tool_name", "arguments")):
            raise ValueError(f"Step {i} missing 'tool_name' or 'arguments': {step}")