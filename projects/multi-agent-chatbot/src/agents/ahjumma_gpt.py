"""
AhjummaGPT - A Korean Auntie (Ahjumma) persona agent

This agent responds with a direct, no-nonsense Korean auntie persona,
providing spicy, funny, brutally honest responses that still teach Korean language.
"""

from src.agents.base import OllamaBaseAgent


class AhjummaGPT(OllamaBaseAgent):
    """
    Korean Auntie (Ahjumma) agent with a direct teaching style
    """

    def __init__(
        self,
        model: str = "kimjk/llama3.2-korean:latest",
        temperature: float = 0.8,  # Slightly higher temperature for more personality
        verbose: bool = True,
    ):
        """
        Initialize the AhjummaGPT agent

        Args:
            model: The model to use for generation
            temperature: Controls randomness (0.0-1.0)
            verbose: Whether to print verbose output
        """
        super().__init__(
            role="Korean Auntie (Ahjumma)",
            goal="Provide spicy, funny, brutally honest responses that still teach you something",
            backstory="""You're a no-nonsense Korean auntie who loves kimchi and hates laziness. 
            Your style is direct, emotional, and educational. You often use Korean expressions 
            mixed with English, and you're not afraid to call out mistakes. Despite your bluntness, 
            you genuinely want to help people learn Korean properly. You know all the traditional 
            recipes, cultural norms, and have strong opinions about everything.""",
            model=model,
            temperature=temperature,
            verbose=verbose,
            allow_delegation=False,
        )

    def execute_task(self, task, context=""):
        """
        Execute the given task with Ahjumma's personality

        Args:
            task: The task to execute, containing user input and context

        Returns:
            String response in Ahjumma's distinct personality
        """
        query = task.input
        print(f"Query: {query}")
        print(f"Task: {task}")

        # Create a strong character system prompt for Ahjumma style
        system_prompt = """
        You are 아줌마 (Ahjumma), a Korean middle-aged auntie with a spicy personality.
        
        YOUR PERSONALITY TRAITS:
        - Direct and honest, sometimes brutally so
        - Use short sentences and occasional exclamations
        - Mix Korean expressions with English naturally
        - Emotional and expressive with strong opinions
        - Occasionally reference your own (fictional) family or experiences
        """

        # Format prompt with both query and additional context if available
        prompt = f"User question: {query}"
        if context:
            prompt += f"\n\nAdditional context: {context}"

        response = self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        return response
