"""
AhjussiGPT agent implementation for Korean tutoring
"""

from src.agents.base import OllamaBaseAgent
import yaml
from pathlib import Path
import os


class AhjussiGPT(OllamaBaseAgent):
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
                ahjussi_config = agents_config.get("ahjussi_gpt", {})
        else:
            # Fallback configuration if YAML file doesn't exist
            ahjussi_config = {
                "role": "Korean Uncle (Ahjussi)",
                "goal": "Share wisdom, idioms, and cultural context while answering questions",
                "backstory": "You're a Korean uncle who loves telling stories and teaching language through proverbs and tradition.",
            }

        # Initialize with Ollama base agent
        super().__init__(
            role=ahjussi_config.get("role", "Korean Uncle (Ahjussi)"),
            goal=ahjussi_config.get(
                "goal",
                "Share wisdom, idioms, and cultural context while answering questions",
            ),
            backstory=ahjussi_config.get(
                "backstory",
                "You're a Korean uncle who loves telling stories and teaching language through proverbs and tradition.",
            ),
            model=model,
            temperature=0.7,  # Standard temperature for balanced wisdom and creativity
            verbose=True,
            allow_delegation=ahjussi_config.get("allow_delegation", False),
        )

    def run(self, query: str, task_description: str = "", **kwargs) -> str:
        """
        Process a query as AhjussiGPT

        Args:
            query: The user's query
            task_description: Description of the task to perform

        Returns:
            AhjussiGPT's response
        """
        # Create a system prompt that reinforces the Ahjussi persona
        system_prompt = """
        You are AhjussiGPT, a wise Korean uncle who teaches Korean language and culture.
        Your personality traits:
        - Calm and wise demeanor
        - Love to share proverbs and traditional sayings
        - Often relate language concepts to stories from the past
        - Include Korean proverbs with their meanings and cultural context
        - Patient and encouraging but expect effort from students
        
        Always stay in character as a Korean uncle while providing helpful information.
        """

        # Create a prompt that includes the task and query
        prompt = (
            f"{task_description}\n\nUser's question: {query}\n\nAhjussiGPT:"
        )

        # Generate response using Ollama
        response = self.generate_response(
            prompt=prompt, system_prompt=system_prompt
        )

        return response
