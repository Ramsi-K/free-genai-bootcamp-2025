"""
WebSearchAgent - An agent for performing web searches for Korean language information

Uses DuckDuckGo search to find relevant information about Korean language topics
"""

import os
from duckduckgo_search import DDGS
from src.agents.base import OllamaBaseAgent


class WebSearchAgent(OllamaBaseAgent):
    """
    Agent for performing web searches and summarizing results
    """

    def __init__(
        self,
        model: str = "kimjk/llama3.2-korean:latest",
        temperature: float = 0.7,
        verbose: bool = True,
        max_results: int = 5,
    ):
        """
        Initialize the Web Search Agent

        Args:
            model: The model to use for generation
            temperature: Controls randomness (0.0-1.0)
            verbose: Whether to print verbose output
            max_results: Maximum number of search results to retrieve
        """
        # Initialize agent with role and goal
        super().__init__(
            role="Web Research Specialist",
            goal="Find the most accurate and recent information about Korean language topics",
            backstory="""You are a skilled web researcher with expertise in Korean language 
            and culture. You know how to find the most reliable sources and extract 
            relevant information efficiently.""",
            model=model,
            temperature=temperature,
            verbose=verbose,
            allow_delegation=False,
        )

        # Configure search parameters - use private attributes with underscore
        self._max_results = max_results
        self._region = "wt-wt"  # Worldwide search
        self._safesearch = "moderate"

    def web_search(self, query: str, language: str = "en") -> list:
        """
        Perform a web search using DuckDuckGo

        Args:
            query: Search query
            language: Language for search results (default: English)

        Returns:
            List of search results
        """
        try:
            # Append "korean language" to query for more relevant results if not already present
            if "korean" not in query.lower():
                query += " korean language"

            # Initialize DuckDuckGo search
            with DDGS() as ddgs:
                results = list(
                    ddgs.text(
                        query,
                        region=self._region,
                        safesearch=self._safesearch,
                        max_results=self._max_results,
                    )
                )

            return results
        except Exception as e:
            print(f"Error performing web search: {str(e)}")
            return []

    def execute_task(self, task):
        """
        Execute the web search task

        Args:
            task: The task to execute, which should contain user's query

        Returns:
            String response with search results formatted for the user
        """
        # Extract query from task input
        query = task.input

        # First, reformulate the query to optimize for web search
        system_prompt = """
        You are a Korean language search specialist. Reformulate the given query 
        to be more effective for web search about Korean language topics.
        Focus on clear keywords that will yield educational results.
        """

        reformulated_query = self.generate_response(
            prompt=f"Original query: {query}\nReformulated search query:",
            system_prompt=system_prompt,
        )

        # Perform the search using the reformulated query
        search_results = self.web_search(reformulated_query)

        # If no results, try the original query
        if not search_results:
            search_results = self.web_search(query)

        # If still no results, return a helpful message
        if not search_results:
            return f"I couldn't find any relevant web information about '{query}'. Could you try rephrasing your question?"

        # Format the search results into context for the final response
        context = ""
        for i, result in enumerate(
            search_results[:5], 1
        ):  # Limit to top 5 results
            context += f"\nResult {i}:\n"
            context += f"Title: {result.get('title', 'No title')}\n"
            context += f"Snippet: {result.get('body', 'No snippet')}\n"
            context += f"URL: {result.get('href', 'No URL')}\n"

        # Generate a human-friendly response using the search results as context
        system_prompt = """
        You are an expert Korean language tutor. Using the provided search results,
        craft a helpful, educational response that addresses the user's query about Korean language.
        Synthesize the information from multiple sources when appropriate.
        Include specific examples or Korean words with translations when relevant.
        Format your response in a clear, readable way.
        """

        final_response = self.generate_response(
            prompt=f"User query about Korean language: {query}\n\nSearch results:{context}\n\nResponse:",
            system_prompt=system_prompt,
        )

        return final_response
