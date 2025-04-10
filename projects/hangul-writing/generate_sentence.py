# generate_sentence.py

import os
import sys
import requests
import subprocess
import json


def generate_sentence(word):
    # Prompt for generating a Korean sentence
    prompt = f"Write a simple Korean sentence (3–5 words) using the word '{word}'. Use basic vocabulary. Do not include English, Chinese characters or any translations. Only output the sentence. Do not explain."

    # Use environment variable for Ollama host or default to localhost
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    model = "kimjk/llama3.2-korean"

    try:
        # First try using the Ollama API (for Docker)
        try:
            response = requests.post(
                f"{ollama_host}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()

        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"API error: {e}. Falling back to CLI.")

        # Fallback to CLI method (for local development)
        command = f'ollama run {model} "{prompt}"'
        output = subprocess.getoutput(command).strip()
        return output

    except Exception as e:
        return f"Error generating sentence: {e}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_sentence.py <word>")
        sys.exit(1)

    word = sys.argv[1]
    sentence = generate_sentence(word)
    print(sentence)
