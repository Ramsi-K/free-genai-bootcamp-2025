import os
import time
import logging
import threading
import sys
import torch
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_caching import Cache
from transformers import BitsAndBytesConfig, pipeline

# Load environment variables
from load_env import load_environment_variables

load_environment_variables()

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

# Create output directory for LLaVA
temp_dir = os.path.join(os.getcwd(), "llava_output")
os.makedirs(temp_dir, exist_ok=True)

# Global variables for LLaVA model loading
model_id = os.environ.get("MODEL_ID", "llava-hf/llava-1.5-7b-hf")


# Function to preload the LLaVA model
def preload_llava_model():
    global llava_model, model_loading_complete, model_loading_error

    # Check if we have API keys for remote inference
    imgbb_api_key = os.environ.get("IMGBB_API_KEY")
    hf_api_key = os.environ.get("HF_API_KEY")

    # If we have the API keys, we don't need to load the model locally
    if imgbb_api_key and hf_api_key:
        logger.info(
            "ImgBB and HuggingFace API keys found. Will use remote inference."
        )
        model_loading_complete = True
        return

    # Otherwise, load the model locally
    logger.info(f"Starting to load the LLaVA model: {model_id}")

    try:
        # Check if CUDA is available
        if torch.cuda.is_available():
            logger.info(f"CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            logger.warning(
                "CUDA not available. Model loading will use CPU and may be slow."
            )

        logger.info("Setting up 4-bit quantization for memory efficiency")
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )

        # Load the model
        try:
            logger.info(f"Loading model {model_id}...")
            pipe = pipeline(
                "image-to-text",
                model=model_id,
                device_map="auto",  # Automatically use GPUs if available
                model_kwargs={
                    "quantization_config": quantization_config,
                    "trust_remote_code": True,
                },
            )
            llava_model = pipe
            logger.info("✅ LLaVA model preloaded successfully")
            model_loading_complete = True
        except Exception as e:
            model_loading_error = str(e)
            logger.error(f"❌ Failed to load LLaVA model: {str(e)}")
    except Exception as e:
        model_loading_error = str(e)
        logger.error(f"❌ Error in preload_llava_model: {str(e)}")


# Start model loading in a separate thread to avoid blocking the server
def start_model_loading():
    thread = threading.Thread(target=preload_llava_model)
    thread.daemon = True
    thread.start()


# Serve the HTML file
@app.route("/")
def index():
    return render_template("Hangul-calligraphy-practice.html")


# API endpoint for checking model status
@app.route("/api/model-status")
def model_status():
    global model_loading_complete, model_loading_error, llava_model

    # Check if we have API keys for remote inference
    imgbb_api_key = os.environ.get("IMGBB_API_KEY")
    hf_api_key = os.environ.get("HF_API_KEY")

    if imgbb_api_key and hf_api_key:
        return jsonify(
            {
                "status": "ready",
                "message": "Using remote inference via HuggingFace API",
                "using_api": True,
            }
        )

    if model_loading_complete:
        return jsonify(
            {
                "status": "ready",
                "message": "Model loaded successfully",
            }
        )
    elif model_loading_error:
        return jsonify(
            {
                "status": "error",
                "message": f"Error loading model: {model_loading_error}",
            }
        )
    else:
        return jsonify(
            {
                "status": "loading",
                "message": "Model is still loading...",
            }
        )


# API endpoint for generating sentences
@cache.cached(timeout=300, query_string=True)
@app.route("/generate-sentence")
def generate_sentence():
    word = request.args.get("word", "")
    
    if not word:
        return jsonify({"sentence": "Please provide a Korean word", "error": "No word provided"})
    
    try:
        # Import the sentence generation function
        from generate_sentence import generate_sentence as gen_sent
        
        # Generate sentence using the imported function
        sentence = gen_sent(word)
        
        return jsonify({"sentence": sentence})
    except Exception as e:
        logger.error(f"Error generating sentence: {e}")
        # Fallback response
        return jsonify(
            {
                "sentence": f"{word}은/는 아름다운 한국어 단어입니다.",
                "error": str(e)
            }
        )


# API endpoint for comparing handwriting
@app.route("/compare-handwriting", methods=["POST"])
def compare_handwriting():
    global llava_model, model_loading_error

    if (
        "reference_image" not in request.files
        or "user_image" not in request.files
    ):
        return (
            jsonify({"error": "Both reference and user images are required"}),
            400,
        )

    try:
        # Get the images
        reference_image = request.files["reference_image"]
        user_image = request.files["user_image"]

        # Create output directory
        temp_dir = os.path.join(os.getcwd(), "llava_output")
        os.makedirs(temp_dir, exist_ok=True)

        # Save images to temporary files
        reference_path = os.path.join(temp_dir, f"ref_{int(time.time())}.jpg")
        user_path = os.path.join(temp_dir, f"user_{int(time.time())}.jpg")

        reference_image.save(reference_path)
        user_image.save(user_path)

        # Check for API keys for remote inference
        imgbb_api_key = os.environ.get("IMGBB_API_KEY")
        hf_api_key = os.environ.get("HF_API_KEY")
        hf_provider = os.environ.get("HF_PROVIDER", "hf")

        # If we have API keys, prefer remote inference
        if imgbb_api_key and hf_api_key:
            logger.info(
                "Starting handwriting comparison using HuggingFace Inference API"
            )

            # Import and use the LLaVA handwriting comparison function
            from simple_llava_handwriting import compare_with_llava_hf_api

            feedback, output_path = compare_with_llava_hf_api(
                reference_path,
                user_path,
                model_id=model_id,
                save_image=True,
                output_dir=temp_dir,
                imgbb_api_key=imgbb_api_key,
                hf_api_key=hf_api_key,
                hf_provider=hf_provider,
            )
        else:
            # Check if LLaVA model is loaded
            if llava_model is None:
                if not model_loading_complete:
                    logger.warning(
                        "LLaVA model not loaded yet, starting loading process..."
                    )
                    start_model_loading()
                    return (
                        jsonify(
                            {
                                "feedback": "Model is still loading. Please try again in a few minutes.",
                                "status": "model_loading",
                            }
                        ),
                        202,
                    )  # 202 Accepted but processing
                elif model_loading_error:
                    logger.error(
                        f"LLaVA model failed to load: {model_loading_error}"
                    )
                    return (
                        jsonify(
                            {
                                "feedback": f"Unable to use LLaVA model. Error: {model_loading_error}",
                                "status": "error",
                            }
                        ),
                        500,
                    )

            # Import and use the LLaVA handwriting comparison function
            from simple_llava_handwriting import (
                compare_with_llava,
                compare_with_llava_chat,
            )

            logger.info(
                "Starting handwriting comparison using local LLaVA model"
            )

            # First try the chat format, which works with newer models
            try:
                feedback, output_path = compare_with_llava_chat(
                    reference_path,
                    user_path,
                    preloaded_model=llava_model,
                    save_image=True,
                    output_dir=temp_dir,
                )
            except Exception as e:
                logger.warning(
                    f"Chat format failed, trying standard format: {str(e)}"
                )
                # Fall back to standard format if chat format fails
                feedback, output_path = compare_with_llava(
                    reference_path,
                    user_path,
                    preloaded_model=llava_model,
                    save_image=True,
                    output_dir=temp_dir,
                )

        # Clean up temporary files
        try:
            os.remove(reference_path)
            os.remove(user_path)
        except Exception as e:
            logger.warning(f"Failed to clean up temporary files: {str(e)}")

        return jsonify(
            {
                "feedback": feedback,
                "image_path": output_path if output_path else None,
                "status": "success",
            }
        )

    except Exception as e:
        logger.error(f"Error in compare_handwriting: {str(e)}")
        return (
            jsonify(
                {
                    "error": str(e),
                    "feedback": "An error occurred while analyzing your handwriting. Please try again.",
                }
            ),
            500,
        )


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
            "model_loaded": llava_model is not None
            or (
                os.environ.get("IMGBB_API_KEY")
                and os.environ.get("HF_API_KEY")
            ),
            "using_api": bool(
                os.environ.get("IMGBB_API_KEY")
                and os.environ.get("HF_API_KEY")
            ),
            "gpu_available": (
                torch.cuda.is_available() if hasattr(torch, "cuda") else False
            ),
        }
    )


if __name__ == "__main__":
    # Start model loading in a background thread
    start_model_loading()

    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "False").lower() == "true"

    logger.info(f"Starting Flask server on port {port} (debug={debug})...")
    app.run(host="0.0.0.0", port=port, debug=debug)
