# server.py

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import subprocess
import tempfile
from werkzeug.utils import secure_filename
import threading
from flask_caching import Cache
import torch
import time
import logging
import sys

# Import our simple comparison function
from simple_compare import simple_compare

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("hangul-app")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize cache
cache = Cache(app, config={"CACHE_TYPE": "simple"})

# Create a module-level variable to store the model
llava_model = None
model_loading_lock = threading.Lock()
model_loading_thread = None
model_loading_error = None
model_loading_complete = False


# Function to preload the LLaVA model
def preload_llava_model():
    global llava_model, model_loading_error, model_loading_complete
    try:
        from transformers import pipeline, BitsAndBytesConfig
        import torch

        logger.info("Preloading LLaVA model... this may take a few minutes")

        # Verify GPU is available
        if torch.cuda.is_available():
            logger.info(f"GPU detected: {torch.cuda.get_device_name(0)}")
            logger.info(
                f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB"
            )
        else:
            logger.warning(
                "No GPU detected! Using CPU which will be very slow."
            )

        # Define model paths from environment or use defaults
        model_id = os.environ.get("LLAVA_MODEL_ID", "llava-hf/llava-1.5-7b-hf")
        cache_dir = os.environ.get("MODEL_CACHE_DIR", "cache/models")

        # Check if model exists locally
        local_model_path = os.path.join(
            cache_dir, f"{model_id.split('/')[-1]}-model"
        )
        if os.path.exists(local_model_path):
            logger.info(f"Using locally saved model at {local_model_path}")
            model_id = local_model_path

        # Set up the quantization config for 4-bit loading to reduce memory usage
        logger.info("Setting up 4-bit quantization for memory efficiency")
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16
        )

        # Load the model
        try:
            logger.info(f"Loading model {model_id}...")
            pipe = pipeline(
                "image-to-text",
                model=model_id,
                device_map="auto",  # Automatically use GPUs if available
                model_kwargs={"quantization_config": quantization_config},
                trust_remote_code=True,
            )
            llava_model = pipe
            logger.info("✅ LLaVA model preloaded successfully")
            model_loading_complete = True
        except Exception as e:
            model_loading_error = str(e)
            logger.error(f"❌ Error loading model: {e}")

    except ImportError as e:
        model_loading_error = f"Missing dependencies: {str(e)}"
        logger.error(f"❌ Error importing dependencies: {e}")
        logger.error(
            "Please run 'pip install -r requirements.txt' or use the conda setup script"
        )
    except Exception as e:
        model_loading_error = str(e)
        logger.error(f"❌ Unexpected error during model loading: {e}")


# Start model loading in a separate thread to avoid blocking the server
def start_model_loading():
    global model_loading_thread
    with model_loading_lock:
        if model_loading_thread is None or not model_loading_thread.is_alive():
            model_loading_thread = threading.Thread(target=preload_llava_model)
            model_loading_thread.daemon = True
            model_loading_thread.start()


# Serve the HTML file
@app.route("/")
def index():
    return render_template("index.html")


# API endpoint for checking model status
@app.route("/api/model-status")
def model_status():
    global model_loading_error, model_loading_complete

    if llava_model is not None:
        return jsonify({"status": "ready"})
    elif model_loading_error:
        return jsonify({"status": "error", "message": model_loading_error})
    elif model_loading_thread and model_loading_thread.is_alive():
        return jsonify({"status": "loading"})
    else:
        return jsonify({"status": "not_started"})


# API endpoint for generating sentences
@cache.cached(timeout=300, query_string=True)
@app.route("/generate-sentence")
def generate_sentence():
    level = request.args.get("level", "beginner")
    theme = request.args.get("theme", "daily life")

    # Use Ollama for Korean sentence generation
    try:
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

        prompt = f"""Generate one simple Korean sentence at {level} level about '{theme}'.
        Include the sentence in Hangul, its English translation, and romanization.
        Format your response as JSON like this:
        {{
          "korean": "한국어 문장",
          "english": "English translation",
          "romanization": "Hangugeo munjang"
        }}"""

        import requests

        response = requests.post(
            f"{ollama_host}/api/generate",
            json={
                "model": "kimjk/llama3.2-korean",  # or other Korean-capable model
                "prompt": prompt,
                "stream": False,
            },
            timeout=30,
        )

        if response.status_code == 200:
            # Parse JSON from the response
            import re
            import json

            result = response.json()
            text = result.get("response", "")

            # Extract JSON from text if needed
            json_match = re.search(r"{[\s\S]*}", text)
            if json_match:
                try:
                    sentence_data = json.loads(json_match.group(0))
                    return jsonify(sentence_data)
                except:
                    pass

            # Fallback for failure to parse
            return jsonify(
                {
                    "korean": "안녕하세요",
                    "english": "Hello",
                    "romanization": "Annyeonghaseyo",
                }
            )
        else:
            # If Ollama fails, provide a default response
            return jsonify(
                {
                    "korean": "안녕하세요",
                    "english": "Hello",
                    "romanization": "Annyeonghaseyo",
                }
            )

    except Exception as e:
        logger.error(f"Error generating sentence: {e}")
        return jsonify(
            {
                "korean": "안녕하세요",
                "english": "Hello",
                "romanization": "Annyeonghaseyo",
                "error": str(e),
            }
        )


# API endpoint for comparing handwriting
@app.route("/compare-handwriting", methods=["POST"])
def compare_handwriting():
    global llava_model, model_loading_error

    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    try:
        # Get the image file and target text
        image_file = request.files["image"]
        target_text = request.form.get("target", "안녕하세요")

        # Save the image to a temporary file
        temp_dir = os.path.join(os.getcwd(), "llava_output")
        os.makedirs(temp_dir, exist_ok=True)

        # Create a unique filename
        filename = secure_filename(
            f"hangul_{int(time.time())}_{hash(target_text)}.jpg"
        )
        image_path = os.path.join(temp_dir, filename)
        image_file.save(image_path)

        # Check if we have LLaVA model loaded
        if llava_model is None:
            # If model is not loaded, try using the simple comparison
            logger.warning("LLaVA model not loaded, using simple comparison")
            result = simple_compare(image_path, target_text)
            return jsonify(
                {
                    "recognized": target_text,
                    "score": result["score"],
                    "feedback": "Using simple comparison (LLaVA model not loaded)",
                }
            )

        # Use LLaVA model for comparison
        prompt = f"What Korean characters are written in this image? Look carefully at the handwritten text and tell me only the exact Korean characters you see, nothing else."

        # Run inference
        result = llava_model(image_path, prompt)

        if isinstance(result, list) and len(result) > 0:
            recognized_text = result[0].get("generated_text", "")

            # Extract only Korean characters from the response
            import re

            korean_chars = re.findall(r"[가-힣]+", recognized_text)
            recognized = (
                "".join(korean_chars)
                if korean_chars
                else "Unable to recognize text"
            )

            # Compare with target
            similarity = simple_compare(
                image_path, target_text, recognized_text=recognized
            )

            return jsonify(
                {
                    "recognized": recognized,
                    "target": target_text,
                    "score": similarity["score"],
                    "feedback": f"Recognized: {recognized}",
                }
            )
        else:
            logger.error("Unexpected model output format")
            return jsonify({"error": "Model returned unexpected format"}), 500

    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return jsonify({"error": str(e)}), 500


# Serve static files
@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)


# Health check endpoint
@app.route("/health")
def health_check():
    return jsonify(
        {
            "status": "healthy",
            "model_loaded": llava_model is not None,
            "gpu_available": (
                torch.cuda.is_available()
                if torch.__name__ == "torch"
                else False
            ),
        }
    )


if __name__ == "__main__":
    # Start model loading in a background thread
    start_model_loading()
    logger.info("Starting Flask server...")
    app.run(host="0.0.0.0", port=5000, debug=False)
