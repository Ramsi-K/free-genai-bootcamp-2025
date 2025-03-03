from flask import Flask, jsonify, request
import requests
import json

app = Flask(__name__)

# In-memory storage
vocab_groups = []

# Fallback data
FALLBACK_DATA = {
    "name": "Food",
    "description": "Words related to Food in Korean",
    "words": [
        {
            "hangul": "김치",
            "romanization": "gimchi",
            "type": "noun",
            "english": ["kimchi", "fermented cabbage"],
            "example_sentence": {
                "korean": "한국 사람들은 매일 김치를 먹어요.",
                "english": "Korean people eat kimchi every day.",
            },
        },
        {
            "hangul": "밥",
            "romanization": "bap",
            "type": "noun",
            "english": ["rice", "meal"],
            "example_sentence": {
                "korean": "저는 매일 아침에 밥을 먹어요.",
                "english": "I eat rice every morning.",
            },
        },
        {
            "hangul": "국수",
            "romanization": "guksu",
            "type": "noun",
            "english": ["noodles"],
            "example_sentence": {
                "korean": "더운 날에는 차가운 국수가 맛있어요.",
                "english": "Cold noodles are delicious on hot days.",
            },
        },
    ],
}

@app.route('/health')
def health():
    # Check Ollama connection
    try:
        response = requests.get("http://ollama-server:11434/api/version")
        return jsonify({
            "status": "healthy",
            "ollama": "connected",
            "ollama_version": response.json().get("version")
        })
    except Exception as e:
        return jsonify({
            "status": "healthy",
            "ollama": "disconnected",
            "error": str(e)
        })

@app.route('/')
def home():
    return jsonify({"message": "Korean Vocabulary Importer"})

@app.route('/models', methods=['GET'])
def list_models():
    try:
        response = requests.get("http://ollama-server:11434/api/tags")
        if response.status_code == 200:
            return jsonify(response.json())
        return jsonify({"error": f"Failed to get models: {response.status_code}"})
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"})

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    theme = data.get("theme", "General")
    count = data.get("count", 5)
    model = data.get("model", "llama3.2:1b")  # Default model
    
    try:
        # Check available models
        models_response = requests.get("http://ollama-server:11434/api/tags")
        models = models_response.json().get("models", [])
        model_names = [m.get("name") for m in models]
        
        # If requested model doesn't exist, use first available
        if model not in model_names and model_names:
            model = model_names[0]
        
        # Generate with Ollama
        prompt = f"""Generate {count} Korean vocabulary words about '{theme}'.
Format the response as a valid JSON object with the following structure:
{{
  "name": "{theme}",
  "description": "Words related to {theme} in Korean",
  "words": [
    {{
      "hangul": "Korean word in Hangul",
      "romanization": "Romanized version", 
      "type": "noun/verb/adjective/etc.",
      "english": ["Primary meaning", "Alternative meaning if applicable"],
      "example_sentence": {{
        "korean": "Example sentence in Korean using the word",
        "english": "English translation of the example sentence"
      }}
    }}
  ]
}}
Ensure it is valid JSON format."""
        
        response = requests.post(
            "http://ollama-server:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            try:
                # Extract JSON from response text
                response_text = response.json().get("response", "")
                
                # Try to find JSON in the response
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    result = json.loads(json_str)
                    
                    # Add model used to response
                    result["model_used"] = model
                    
                    vocab_groups.append(result)
                    return jsonify(result)
            except Exception as e:
                # JSON extraction failed
                print(f"Error extracting JSON: {str(e)}")
                
        # Fallback to default data
        result = dict(FALLBACK_DATA)
        result["name"] = theme
        result["description"] = f"Words related to {theme} in Korean (fallback data)"
        result["model_used"] = "fallback"
        
        vocab_groups.append(result)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        # Use fallback data on error
        result = dict(FALLBACK_DATA)
        result["name"] = theme
        result["description"] = f"Words related to {theme} in Korean (error occurred: {str(e)})"
        
        vocab_groups.append(result)
        return jsonify(result)

@app.route('/groups', methods=['GET'])
def list_groups():
    return jsonify(vocab_groups)

@app.route('/export/<int:index>', methods=['GET'])
def export_group(index):
    if index < 0 or index >= len(vocab_groups):
        return jsonify({"error": "Group not found"}), 404
    return jsonify(vocab_groups[index])

@app.route('/import', methods=['POST'])
def import_group():
    group = request.get_json()
    vocab_groups.append(group)
    return jsonify(group)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
