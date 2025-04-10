# server.py

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import subprocess
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# Serve the HTML file
@app.route("/")
def index():
    return render_template("Hangul-calligraphy-practice.html")


# API endpoint for generating sentences
@app.route("/generate-sentence")
def generate_sentence():
    word = request.args.get("word", "")
    if not word:
        return jsonify({"error": "No word provided"}), 400

    try:
        # Call the generate_sentence.py script
        result = subprocess.check_output(
            ["python", "generate_sentence.py", word],
            text=True,
            stderr=subprocess.STDOUT,
        )
        return jsonify({"sentence": result.strip()})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e.output)}), 500


# API endpoint for comparing handwriting
@app.route("/compare-handwriting", methods=["POST"])
def compare_handwriting():
    # Check if both images were uploaded
    if (
        "reference_image" not in request.files
        or "user_image" not in request.files
    ):
        return jsonify({"error": "Missing reference or user image"}), 400

    try:
        # Create temporary directory for the images
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the uploaded files
            ref_image = request.files["reference_image"]
            user_image = request.files["user_image"]

            ref_path = os.path.join(temp_dir, "reference.png")
            user_path = os.path.join(temp_dir, "user.png")

            ref_image.save(ref_path)
            user_image.save(user_path)

            # Call the LLaVA comparison script
            cmd = ["python", "compare_with_llava.py"]
            process = subprocess.Popen(
                cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
            )

            # Provide the image paths when requested
            stdout, _ = process.communicate(f"{ref_path}\n{user_path}\n")

            # Parse the output for feedback
            feedback_start = stdout.find("=== LLaVA Feedback ===")
            if feedback_start != -1:
                feedback = stdout[
                    feedback_start + len("=== LLaVA Feedback ===") :
                ].strip()
            else:
                feedback = "Analysis complete, but no feedback was provided."

            return jsonify({"feedback": feedback})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Serve static files
@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)


# Serve the llava_output directory
@app.route("/llava_output/<path:path>")
def serve_llava_output(path):
    return send_from_directory("llava_output", path)


if __name__ == "__main__":
    # Ensure output directory exists
    os.makedirs("llava_output", exist_ok=True)

    # Move HTML template to templates folder
    os.makedirs("templates", exist_ok=True)
    if not os.path.exists(
        "templates/Hangul-calligraphy-practice.html"
    ) and os.path.exists("Hangul-calligraphy-practice.html"):
        import shutil

        shutil.copy(
            "Hangul-calligraphy-practice.html",
            "templates/Hangul-calligraphy-practice.html",
        )

    # Run the app on 0.0.0.0 to make it accessible from outside the container
    app.run(debug=True, port=5000, host="0.0.0.0")
