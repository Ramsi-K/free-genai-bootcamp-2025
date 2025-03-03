import requests

print("Testing connection to Ollama...")
try:
    response = requests.get("http://ollama-server:11434/api/version")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {str(e)}")
