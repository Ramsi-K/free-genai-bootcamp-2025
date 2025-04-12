# web_agent.py

"""
Agent that uses DuckDuckGo to perform web search.
Requires: pip install -U duckduckgo-search
"""

from typing import List, Dict, Optional
from duckduckgo_search import DDGS

class WebSearchAgent:
    def __init__(self, source: str = "text", region: str = "wt-wt", safesearch: str = "moderate", max_results: int = 5):
        self.source = source
        self.region = region
        self.safesearch = safesearch
        self.max_results = max_results

    def search(self, query: str) -> List[Dict[str, str]]:
        with DDGS() as ddgs:
            if self.source == "text":
                return list(ddgs.text(query, region=self.region, safesearch=self.safesearch, max_results=self.max_results))
            elif self.source == "news":
                return list(ddgs.news(query, region=self.region, safesearch=self.safesearch, max_results=self.max_results))
            elif self.source == "images":
                return list(ddgs.images(query, region=self.region, safesearch=self.safesearch, max_results=self.max_results))
            else:
                return []

    def search_summary(self, query: str) -> str:
        results = self.search(query)
        if not results:
            return "No good DuckDuckGo Search Result was found"
        return "\n".join([f"{r.get('title', '')}: {r.get('body', '') or r.get('snippet', '')}" for r in results])
