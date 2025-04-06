from ...base.base_tool import BaseTool
from duckduckgo_search import DDGS
import logging


class WebSearchTool(BaseTool):
    def __init__(self):
        self.logger = logging.getLogger()

    def run(self, input_data: dict) -> dict:
        query = input_data.get("query", "")
        self.logger.info(f"Querying DuckDuckGo: {query}")

        with DDGS() as ddgs:
            results = [r["body"] for r in ddgs.text(query, max_results=3)]
        self.logger.info(f"Query results: {results}")
        return {"results": results}