import requests
import sys
import time

def test_ollama(url="http://localhost:11434", model="kimjk/llama3.2-korean:latest"):
    print(f"Testing connection to Ollama at {url} using model {model}...")
    
    # First test API availability without model
    try:
        response = requests.get(f"{url}/api/tags")
        if response.status_code == 200:
            print("✅ Ollama API is accessible!")
            print("Available models:", response.json())
        else:
            print(f"❌ Error: Ollama API returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Ollama API: {e}")
        return False
    
    # Now test with a very simple prompt (not using the model for inference yet)
    try:
        print(f"\nTesting with a minimal prompt to model {model}...")
        
        start_time = time.time()
        response = requests.post(
            f"{url}/api/generate",
            json={"model": model, "prompt": "hi", "stream": False, "options": {"num_predict": 1}},
            timeout=30  # Extended timeout
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Model responded in {elapsed:.2f} seconds!")
            return True
        else:
            print(f"❌ Error: Model returned status code {response.status_code}")
            print(response.text)
            return False
    except requests.exceptions.Timeout:
        print(f"❌ Error: Request timed out after 30 seconds")
        print("The model might be loading or is too large for quick responses")
        return False
    except Exception as e:
        print(f"❌ Error testing model: {e}")
        return False

if __name__ == "__main__":
    url = "http://localhost:11434"
    model = "kimjk/llama3.2-korean:latest"
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    if len(sys.argv) > 2:
        model = sys.argv[2]
    
    test_ollama(url, model)