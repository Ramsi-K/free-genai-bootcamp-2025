"""
Vector Database Agent - An agent for retrieving knowledge from a vector database

This agent provides natural language interaction with the vector database,
allowing for semantic search and knowledge retrieval.
"""

import os
from src.agents.base import OllamaBaseAgent
from src.tools.vector_db_tool import VectorDBTool


class VectorDBAgent(OllamaBaseAgent):
    """
    Agent for querying the vector database using natural language
    """

    def __init__(
        self,
        model: str = "kimjk/llama3.2-korean:latest",
        temperature: float = 0.7,
        verbose: bool = True,
    ):
        """
        Initialize the Vector Database Agent

        Args:
            model: The model to use for generation
            temperature: Controls randomness (0.0-1.0)
            verbose: Whether to print verbose output
        """
        # Get configuration from environment or use defaults
        db_url = os.environ.get("QDRANT_URL")
        collection_name = os.environ.get(
            "QDRANT_COLLECTION", "korean_language_learning"
        )

        # Initialize agent with role and goal
        super().__init__(
            role="Knowledge Retrieval Specialist",
            goal="Find the most relevant information from the knowledge base",
            backstory="""You are a highly efficient knowledge retrieval specialist with 
            access to a vast database of Korean language learning resources. Your expertise 
            lies in finding the most relevant examples, explanations, and materials to help 
            users understand Korean language concepts.""",
            model=model,
            temperature=temperature,
            verbose=verbose,
            allow_delegation=False,
        )

        # Initialize vector database tool - using _vector_db_tool instead of vector_db_tool
        self._vector_db_tool = VectorDBTool(
            db_url=db_url,
            collection_name=collection_name,
        )

    def execute_task(self, task):
        """
        Execute the vector database search task

        Args:
            task: The task to execute, which should contain user's query

        Returns:
            String response with search results formatted for the user
        """
        # Extract query from task input
        if hasattr(task, "input"):
            query = task.input
            context = getattr(task, "context", None)
        else:
            query = task.get("input", "")
            context = task.get("context", None)

        # First, reformulate the query to optimize for vector search
        system_prompt = """
        You are a Korean language search specialist. Reformulate the given query 
        to be more effective for semantic vector search in a Korean language learning database.
        Focus on extracting key concepts, grammar points, or vocabulary.
        """

        reformulated_query = self.generate_response(
            prompt=f"Original query: {query}\nReformulated search query:",
            system_prompt=system_prompt,
        )

        # Perform the search using the reformulated query
        results = self._vector_db_tool.search(reformulated_query)

        # If no results, try the original query
        if not results:
            results = self._vector_db_tool.search(query)

        # If still no results, return a helpful message
        if not results:
            return f"I couldn't find any relevant information about '{query}' in my knowledge base. Could you try rephrasing your question?"

        # Format the search results into context for the final response
        context = ""
        for i, result in enumerate(results[:5], 1):  # Limit to top 5 results
            context += f"\nResource {i}:\n"
            context += f"Text: {result['text']}\n"
            if "metadata" in result and result["metadata"]:
                if "source" in result["metadata"]:
                    context += f"Source: {result['metadata']['source']}\n"
                if "chapter" in result["metadata"]:
                    context += f"Chapter: {result['metadata']['chapter']}\n"

        # Generate a human-friendly response using the search results as context
        system_prompt = """
        You are an expert Korean language tutor. Using the provided search results,
        craft a helpful, concise response that addresses the user's query.
        Include specific examples from the resources when relevant.
        When appropriate, add Korean text with English translations.
        Format your response in a clear, readable way.
        """

        final_response = self.generate_response(
            prompt=f"User query: {query}\n\nSearch results:{context}\n\nResponse:",
            system_prompt=system_prompt,
        )

        return final_response
