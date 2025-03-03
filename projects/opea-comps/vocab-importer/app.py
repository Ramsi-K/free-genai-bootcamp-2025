from flask import Flask, jsonify, request, send_from_directory
import requests
import json
import os
import time

app = Flask(__name__, static_folder="static")

# Create static folder if it doesn't exist
os.makedirs(app.static_folder, exist_ok=True)

# In-memory storage
vocab_groups = []

# Fallback data
FALLBACK_DATA = {
    "name": "Food",
    "description": "Words related to Food",
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


@app.route("/health")
def health():
    # Check Ollama connection
    try:
        response = requests.get("http://ollama-server:11434/api/version")
        return jsonify(
            {
                "status": "healthy",
                "ollama": "connected",
                "ollama_version": response.json().get("version"),
            }
        )
    except Exception as e:
        return jsonify(
            {"status": "healthy", "ollama": "disconnected", "error": str(e)}
        )


@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/models", methods=["GET"])
def list_models():
    try:
        response = requests.get("http://ollama-server:11434/api/tags")
        if response.status_code == 200:
            return jsonify(response.json())
        return jsonify(
            {"error": f"Failed to get models: {response.status_code}"}
        )
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"})


def parse_llm_json(text):
    """
    Advanced function to parse JSON from LLM responses.
    Handles common issues like multiline strings, unicode, etc.
    """
    # First, try to extract JSON from the text
    json_start = text.find("{")
    json_end = text.rfind("}") + 1

    if json_start >= 0 and json_end > json_start:
        json_str = text[json_start:json_end]

        # Try different parsing strategies
        # 1. Direct JSON parse
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"First JSON parse attempt failed: {e}")

        # 2. Replace newlines and try again
        try:
            cleaned = json_str.replace("\n", "\\n")
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"Second JSON parse attempt failed: {e}")

        # 3. Try with AST literal_eval which is more forgiving
        try:
            import ast

            return ast.literal_eval(json_str)
        except Exception as e:
            print(f"AST parsing failed: {e}")

        # 4. Use regex to extract the JSON structure (simple approach)
        try:
            import re

            # Find the outermost braces and everything inside them
            match = re.search(r"\{.*\}", json_str, re.DOTALL)
            if match:
                matched_json = match.group(0)
                return json.loads(matched_json)
        except Exception as e:
            print(f"Regex extraction failed: {e}")

    return None


@app.route("/generate", methods=["POST"])
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

        print(
            f"Using model: {model} to generate {count} words about '{theme}'"
        )

        # Generate with Ollama
        prompt = f"""Generate {count} Korean vocabulary words about '{theme}'.

You must respond with ONLY a valid JSON object and nothing else.
No explanations, no markdown formatting, no code blocks.
Just return a raw, valid JSON object with the following structure:

{{
  "name": "{theme}",
  "description": "Words related to {theme}",
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

IMPORTANT: 
1. Escape all special characters properly
2. Make sure it is valid JSON that can be parsed with json.loads()
3. Avoid any line breaks in strings - replace them with \\n
4. Make sure all quotes are properly escaped
5. DO NOT include any other text outside the JSON object"""

        response = requests.post(
            "http://ollama-server:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
        )

        if response.status_code == 200:
            try:
                # Get full response and log it for debugging
                response_data = response.json()
                response_text = response_data.get("response", "")
                print(f"Raw response from {model}:\n{response_text}\n")

                # Use our advanced parser
                result = parse_llm_json(response_text)

                if result:
                    print("Successfully parsed JSON using advanced parser")

                    # Add model used to response
                    result["model_used"] = model

                    # Validate the result has the expected structure
                    if (
                        "name" in result
                        and "description" in result
                        and "words" in result
                    ):
                        print("Valid vocabulary structure found")
                        vocab_groups.append(result)
                        return jsonify(result)
                    else:
                        print("Invalid structure in parsed result")
                else:
                    print("Advanced JSON parsing failed")

                # If we get here, try direct curl-style approach
                # This is a more direct approach used by your curl command
                direct_prompt = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                }

                print("Trying direct API approach...")
                direct_response = requests.post(
                    "http://ollama-server:11434/api/generate",
                    json=direct_prompt,
                )

                if direct_response.status_code == 200:
                    direct_text = direct_response.json().get("response", "")
                    direct_result = parse_llm_json(direct_text)

                    if direct_result:
                        print("Direct approach succeeded")
                        direct_result["model_used"] = model
                        vocab_groups.append(direct_result)
                        return jsonify(direct_result)

            except Exception as e:
                # JSON extraction failed
                print(f"Error processing response: {str(e)}")
        else:
            print(f"Error from Ollama API: {response.status_code}")
            print(response.text)

        # If all else fails, fallback to default data
        result = dict(FALLBACK_DATA)
        result["name"] = theme
        result["description"] = f"Words related to {theme} (fallback data)"
        result["model_used"] = "fallback"

        vocab_groups.append(result)
        return jsonify(result)

    except Exception as e:
        print(f"Error: {str(e)}")
        # Use fallback data on error
        result = dict(FALLBACK_DATA)
        result["name"] = theme
        result["description"] = (
            f"Words related to {theme} (error occurred: {str(e)})"
        )

        vocab_groups.append(result)
        return jsonify(result)


@app.route("/groups", methods=["GET"])
def list_groups():
    return jsonify(vocab_groups)


@app.route("/export/<int:index>", methods=["GET"])
def export_group(index):
    if index < 0 or index >= len(vocab_groups):
        return jsonify({"error": "Group not found"}), 404
    return jsonify(vocab_groups[index])


@app.route("/import", methods=["POST"])
def import_group():
    group = request.get_json()
    vocab_groups.append(group)
    return jsonify(group)


@app.route("/save", methods=["POST"])
def save_vocab():
    vocab_data = request.get_json()
    theme = vocab_data.get("name", "unknown")
    filename = (
        f"data/{theme.lower().replace(' ', '-')}-{int(time.time())}.json"
    )

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(vocab_data, f, ensure_ascii=False, indent=2)

    return jsonify({"success": True, "filename": filename})


@app.route("/debug", methods=["GET"])
def debug_info():
    """Endpoint to get debugging information and test the API directly"""
    try:
        # Check Ollama connection
        ollama_status = {}
        try:
            response = requests.get("http://ollama-server:11434/api/version")
            ollama_status = {
                "connected": True,
                "version": response.json().get("version"),
            }
        except Exception as e:
            ollama_status = {"connected": False, "error": str(e)}

        # Get available models
        models = []
        try:
            response = requests.get("http://ollama-server:11434/api/tags")
            models = response.json().get("models", [])
        except Exception:
            pass

        # Test API with a simple prompt
        test_result = {}
        try:
            response = requests.post(
                "http://ollama-server:11434/api/generate",
                json={
                    "model": models[0]["name"] if models else "llama3.2:1b",
                    "prompt": "Return the text 'Hello World' as JSON with the key 'message'",
                    "stream": False,
                },
            )
            test_result = {
                "status_code": response.status_code,
                "response": (
                    response.json() if response.status_code == 200 else None
                ),
            }
        except Exception as e:
            test_result = {"error": str(e)}

        return jsonify(
            {
                "ollama_status": ollama_status,
                "models": models,
                "test_result": test_result,
                "vocab_groups": vocab_groups,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
