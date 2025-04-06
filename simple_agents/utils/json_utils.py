import re
import json


def extract_json(content):
    # Strip <think> tags or other non-JSON stuff
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
    if content.strip().startswith("```json"):
        content = re.sub(r"```json|```", "", content).strip()
    return json.loads(content)
