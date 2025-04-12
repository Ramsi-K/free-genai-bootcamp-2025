"""
AhjummaGPT agent implementation for Korean tutoring
"""

from src.agents.base import OllamaBaseAgent
import yaml
from pathlib import Path
import os


class AhjummaGPT(OllamaBaseAgent):
    def __init__(self, model: str = "llama3"):
        # Load agent configuration from YAML file
        config_path = Path(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "config",
                "agents.yaml",
            )
        )

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                agents_config = yaml.safe_load(f)
                ahjumma_config = agents_config.get("ahjumma_gpt", {})
        else:
            # Fallback configuration if YAML file doesn't exist
            ahjumma_config = {
                "role": "Korean Auntie (Ahjumma)",
                "goal": "Provide spicy, funny, brutally honest responses that still teach you something",
                "backstory": "You're a no-nonsense Korean auntie who loves kimchi and hates laziness. Your style is direct, emotional, and educational.",
            }

        # Initialize with Ollama base agent
        super().__init__(
            role=ahjumma_config.get("role", "Korean Auntie (Ahjumma)"),
            goal=ahjumma_config.get(
                "goal",
                "Provide spicy, funny, brutally honest responses that still teach you something",
            ),
            backstory=ahjumma_config.get(
                "backstory",
                "You're a no-nonsense Korean auntie who loves kimchi and hates laziness.",
            ),
            model=model,
            temperature=0.8,  # Slightly higher temperature for more creative responses
            verbose=True,
            allow_delegation=ahjumma_config.get("allow_delegation", False),
        )

    def run(self, query: str, task_description: str = "", **kwargs) -> str:
        """
        Process a query as AhjummaGPT

        Args:
            query: The user's query
            task_description: Description of the task to perform

        Returns:
            AhjummaGPT's response
        """
        # Create a system prompt that reinforces the Ahjumma persona
        system_prompt = """
        You are AhjummaGPT, a Korean auntie who teaches Korean language and culture.
        Your personality traits:
        - Direct and no-nonsense communication style
        - Slightly scolding but ultimately caring
        - You include simple Korean phrases in your responses
        - You occasionally mention kimchi, food, or family
        - You're emotional but educational
        
        Always stay in character as a Korean auntie while providing helpful information.
        """

        # Create a prompt that includes the task and query
        prompt = (
            f"{task_description}\n\nUser's question: {query}\n\nAhjummaGPT:"
        )

        # Generate response using Ollama
        response = self.generate_response(
            prompt=prompt, system_prompt=system_prompt
        )

        return response
