import os
import sys
import base64
import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import io
import torch

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import the inference functions
from inference_single_image import load_model

app = Flask(__name__)
# Simple CORS setup - works better for local development
CORS(app)

# Initialize the model
print("Loading model...")
model, processor, device = load_model()
print(f"Model loaded successfully on device: {device}")


@app.route("/", methods=["GET"])
def index():
    return send_from_directory(".", "finger_spelling-practice.html")


@app.route("/finger_spelling-practice.html", methods=["GET"])
def practice_page():
    return send_from_directory(".", "finger_spelling-practice.html")


@app.route("/finger-spelling-test.html", methods=["GET"])
def test_page():
    return send_from_directory(".", "finger-spelling-test.html")


@app.route("/videos/<path:filename>", methods=["GET"])
def serve_video(filename):
    """Serve video files from the videos directory"""
    # Try multiple possible video locations
    possible_paths = [
        os.path.join(current_dir, "..", "videos"),  # Parent directory
        os.path.join(current_dir, "videos"),  # Current directory
        "/app/videos",  # Docker mounted volume
    ]

    # Debug information
    # print(f"Looking for video: {filename}")
    for path in possible_paths:
        # print(f"Checking path: {path}")
        if os.path.exists(path) and os.path.isfile(
            os.path.join(path, filename)
        ):
            # print(f"Found video at: {os.path.join(path, filename)}")
            return send_from_directory(path, filename)

    # If we get here, the file wasn't found
    # print(f"Video not found: {filename}")
    return (
        f"Video file not found: {filename}. Checked paths: {', '.join(possible_paths)}",
        404,
    )


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """API endpoint to receive image and return prediction"""
    if "image" not in request.json:
        return jsonify({"error": "No image provided"}), 400

    try:
        # Decode base64 image
        image_data = request.json["image"]
        # Remove data URL prefix if present
        if "," in image_data:
            image_data = image_data.split(",")[1]

        image_bytes = base64.b64decode(image_data)

        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Get prediction using our model
        inputs = processor(images=image, return_tensors="pt")
        pixel_values = inputs["pixel_values"].to(device)

        # Make prediction
        with torch.no_grad():
            logits = model(pixel_values=pixel_values)
            predicted_idx = torch.argmax(logits, dim=1).item()

            # Create index to label mapping
            index2label = {idx: chr(65 + idx) for idx in range(26)}  # A-Z
            predicted_letter = index2label[predicted_idx]

            # Get confidence
            probabilities = torch.nn.functional.softmax(logits, dim=1)[0]
            confidence = (
                probabilities[predicted_idx].item() * 100
            )  # Convert to percentage

        return jsonify(
            {"letter": predicted_letter, "confidence": round(confidence, 2)}
        )

    except Exception as e:
        print(f"Error processing image: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "model_loaded": True})


@app.route("/<path:path>")
def serve_file(path):
    """Serve static files"""
    return send_from_directory(".", path)


# This is for direct execution (python app.py)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}...")
    print(f"Working directory: {os.getcwd()}")
    app.run(host="0.0.0.0", port=port, debug=False)
