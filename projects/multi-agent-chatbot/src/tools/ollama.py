"""
OllamaTool - A tool for interfacing with the Ollama API

This tool provides a simple interface for generating text and conducting
chat conversations with Ollama-hosted language models.
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional


class OllamaTool:
    """
    A tool for interacting with Ollama API for text generation and chat
    """

    def __init__(
        self,
        model: str = "kimjk/llama3.2-korean:latest",
        host: Optional[str] = None,
        port: Optional[str] = None,
    ):
        """
        Initialize the Ollama tool

        Args:
            model: The model to use for generation
            host: Ollama host (defaults to OLLAMA_HOST env var or 'ollama')
            port: Ollama port (defaults to OLLAMA_PORT env var or '11434')
        """
        self.model = model
        self.host = host or os.environ.get("OLLAMA_HOST", "ollama")
        self.port = port or os.environ.get("OLLAMA_PORT", "11434")
        self.base_url = f"http://{self.host}:{self.port}"

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """
        Generate a completion using Ollama API

        Args:
            prompt: The prompt to send to the model
            system_prompt: Optional system prompt to guide the model behavior
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            Dict with response text and metadata
        """
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        # Add system prompt if provided
        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error communicating with Ollama: {str(e)}"}

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Chat with Ollama using a list of messages

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum number of tokens to generate
            system_prompt: Optional system prompt to guide the model behavior

        Returns:
            Dict with the generated message and metadata
        """
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        # Add system prompt if provided
        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error communicating with Ollama: {str(e)}"}
