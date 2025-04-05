from base.base_tool import BaseTool
from duckduckgo_search import DDGS


class WebSearchTool(BaseTool):
    def run(self, input_data: dict) -> dict:
        query = input_data["query"]
        print(f"[WebSearchTool] Querying DuckDuckGo: {query}")

        with DDGS() as ddgs:
            results = [r["body"] for r in ddgs.text(query, max_results=3)]
        return {"results": results}