"""
Base agent class that integrates with Ollama for LLM capabilities
"""

from crewai import Agent
from src.tools.ollama import OllamaTool


class OllamaBaseAgent(Agent):
    """
    Base agent class that integrates with Ollama for LLM capabilities
    """

    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str,
        model: str = "llama3",
        temperature: float = 0.7,
        verbose: bool = True,
        allow_delegation: bool = False,
    ):
        # Initialize Ollama Tool
        self.ollama_tool = OllamaTool(model=model)

        # Initialize agent
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=verbose,
            allow_delegation=allow_delegation,
        )

        # Set agent configuration
        self.temperature = temperature
        self.model = model

    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generate a response using Ollama

        Args:
            prompt: The prompt to send to Ollama
            system_prompt: Optional system prompt to guide the model

        Returns:
            The generated response
        """
        result = self.ollama_tool.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=self.temperature,
        )

        if result.get("error"):
            return f"Error generating response: {result['error']}"

        return result.get("response", "No response generated")

    def chat(self, messages: list) -> str:
        """
        Chat with Ollama using a list of messages

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys

        Returns:
            The generated response
        """
        result = self.ollama_tool.chat(
            messages=messages,
            temperature=self.temperature,
        )

        if result.get("error"):
            return f"Error generating response: {result['error']}"

        return result.get("message", {}).get(
            "content", "No response generated"
        )
