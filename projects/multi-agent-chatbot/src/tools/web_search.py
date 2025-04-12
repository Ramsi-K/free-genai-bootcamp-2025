# src/tools/web_search.py
from typing import List, Dict
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests

class WebSearchAgent:
    def __init__(self, source="text", region="wt-wt", safesearch="moderate", max_results=5):
        self.source = source
        self.region = region
        self.safesearch = safesearch
        self.max_results = max_results

    def search(self, query: str) -> List[Dict]:
        """Perform a web search and return results"""
        with DDGS() as ddgs:
            results = ddgs.search(
                query,
                region=self.region,
                safesearch=self.safesearch,
                max_results=self.max_results
            )
            return [
                {
                    "title": r.title,
                    "url": r.url,
                    "snippet": r.snippet
                }
                for r in results
            ]

    def search_summary(self, query: str) -> str:
        """Return a formatted summary of search results"""
        results = self.search(query)
        if not results:
            return "No results found."
            
        return "\n".join(
            [f"🔗 {r['title']}\n{r['snippet']}\n" for r in results]
        )