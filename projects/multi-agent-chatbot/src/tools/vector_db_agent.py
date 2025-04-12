"""
Vector Database Agent for RAG capabilities using Qdrant
"""

from typing import Dict, Any, List
from crewai import Agent
from src.tools.vector_db import VectorDBTool


class VectorDBAgent(Agent):
    def __init__(self):
        self.vector_db = VectorDBTool()

        super().__init__(
            role="Korean Language Learning Database",
            goal="Retrieve relevant Korean language examples and information from the vector database",
            backstory="""You are a specialized agent that searches the Korean language learning database 
            for examples, idioms, vocabulary, and cultural information to support the learner's queries.""",
            verbose=True,
            allow_delegation=False,
        )

    def retrieve_relevant_content(
        self, query: str, filters: Dict[str, Any] = None, limit: int = 5
    ) -> List[Dict]:
        """
        Retrieve relevant content from the vector database based on the query and optional filters

        Args:
            query: The search query
            filters: Optional filters to apply to the search (e.g., {"topic": "Food"})
            limit: Maximum number of results to return

        Returns:
            List of relevant content items with their metadata
        """
        results = self.vector_db.query(
            query_text=query, filter_by=filters, limit=limit
        )
        return results

    def format_retrieved_content(self, results: List[Dict]) -> str:
        """
        Format the retrieved content into a readable string

        Args:
            results: List of retrieved content items

        Returns:
            Formatted string with retrieved content
        """
        if not results:
            return "No relevant content found in the database."

        formatted_output = "### Retrieved Korean Language Content:\n\n"

        for i, result in enumerate(results):
            formatted_output += (
                f"**Result {i+1}** (Relevance: {result['score']:.2f})\n"
            )
            formatted_output += f"```\n{result['text']}\n```\n"

            if result.get("metadata"):
                metadata = result["metadata"]
                formatted_output += "**Metadata:**\n"

                # Format metadata for better readability
                if metadata.get("persona"):
                    formatted_output += (
                        f"- **Persona**: {metadata['persona']}\n"
                    )
                if metadata.get("tone"):
                    formatted_output += f"- **Tone**: {metadata['tone']}\n"
                if metadata.get("TOPIK_level"):
                    formatted_output += (
                        f"- **TOPIK Level**: {metadata['TOPIK_level']}\n"
                    )
                if metadata.get("topic"):
                    formatted_output += f"- **Topic**: {metadata['topic']}\n"
                if metadata.get("text_source"):
                    formatted_output += (
                        f"- **Source**: {metadata['text_source']}\n"
                    )

            formatted_output += "\n---\n\n"

        return formatted_output

    def run(self, query: str, task_description: str = "", **kwargs) -> str:
        """
        Run the agent with the given query

        Args:
            query: The query to process
            task_description: Description of the task

        Returns:
            The agent's response
        """
        # Extract any filtering parameters from kwargs
        filters = kwargs.get("filters", {})
        limit = kwargs.get("limit", 5)

        # Detect potential topic from query to enhance retrieval
        topic_keywords = {
            "food": [
                "food",
                "eat",
                "recipe",
                "restaurant",
                "김치",
                "밥",
                "음식",
            ],
            "culture": ["culture", "tradition", "custom", "예절", "문화"],
            "grammar": [
                "grammar",
                "verb",
                "noun",
                "sentence",
                "conjugate",
                "문법",
            ],
            "travel": ["travel", "location", "place", "visit", "여행", "장소"],
            "greeting": ["greeting", "hello", "goodbye", "안녕", "인사"],
        }

        # Try to determine a topic from the query
        detected_topic = None
        for topic, keywords in topic_keywords.items():
            if any(keyword.lower() in query.lower() for keyword in keywords):
                detected_topic = topic.capitalize()
                break

        if detected_topic and not filters.get("topic"):
            filters["topic"] = detected_topic

        # Retrieve relevant content
        results = self.retrieve_relevant_content(query, filters, limit)

        # Format the results
        formatted_results = self.format_retrieved_content(results)

        return formatted_results
