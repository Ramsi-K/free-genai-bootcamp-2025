"""
Ollama Tool for LLM capabilities
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List


class OllamaTool:
    def __init__(
        self,
        host: str = None,
        port: str = None,
        model: str = "llama3",
    ):
        # Handle Docker environment variables if specified
        self.host = host or os.getenv("OLLAMA_HOST", "localhost")
        self.port = port or os.getenv("OLLAMA_PORT", "11434")
        self.model = model
        self.base_url = f"http://{self.host}:{self.port}"

        self._ensure_model_available()

    def _ensure_model_available(self):
        """Check if the model is available, pulls it if not"""
        try:
            # List available models
            response = requests.get(f"{self.base_url}/api/tags")

            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [model["name"] for model in models]

                if self.model not in available_models:
                    print(
                        f"Model {self.model} not found. Available models: {', '.join(available_models)}"
                    )
                    print(
                        f"You need to pull the model using: docker exec -it korean-ollama ollama pull {self.model}"
                    )
            else:
                print(
                    f"Failed to check available models: {response.status_code} - {response.text}"
                )

        except Exception as e:
            print(f"Error connecting to Ollama service: {e}")

    def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate text using Ollama

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt to guide the model
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            Dictionary containing the model's response
        """
        try:
            # Prepare the request payload
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }

            if system_prompt:
                payload["system"] = system_prompt

            # Make the API call
            response = requests.post(
                f"{self.base_url}/api/generate", json=payload
            )

            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                print(error_msg)
                return {"error": error_msg, "response": None}

        except Exception as e:
            error_msg = f"Error calling Ollama: {e}"
            print(error_msg)
            return {"error": error_msg, "response": None}

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Chat with Ollama using a list of messages

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            Dictionary containing the model's response
        """
        try:
            # Prepare the request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }

            # Make the API call
            response = requests.post(f"{self.base_url}/api/chat", json=payload)

            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                print(error_msg)
                return {"error": error_msg, "response": None}

        except Exception as e:
            error_msg = f"Error calling Ollama: {e}"
            print(error_msg)
            return {"error": error_msg, "response": None}

    def list_models(self) -> List[str]:
        """
        List available models in Ollama

        Returns:
            List of model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")

            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            else:
                print(
                    f"Failed to list models: {response.status_code} - {response.text}"
                )
                return []

        except Exception as e:
            print(f"Error listing models: {e}")
            return []
