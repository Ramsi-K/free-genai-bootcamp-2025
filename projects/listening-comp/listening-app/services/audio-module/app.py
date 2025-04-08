import os
import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import torch
import sqlite3
from prometheus_client import Counter, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import sys
import scipy.io.wavfile
from transformers import VitsModel, AutoTokenizer

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
)
from services.metrics.persistence import MetricsPersistence

app = Flask(__name__)
CORS(app)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})


# Initialize Prometheus metrics
AUDIO_GENERATED = Counter(
    "audio_generated_total", "Total number of audio files generated"
)
TTS_ERRORS = Counter(
    "tts_errors_total", "Total number of errors during TTS generation"
)

# Add Prometheus metrics endpoint
app.wsgi_app = DispatcherMiddleware(
    app.wsgi_app, {"/metrics": make_wsgi_app()}
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
DATA_DIR = os.environ.get("DATA_DIR", "/shared/data")
AUDIO_DIR = os.path.join(DATA_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Load the Hugging Face model and tokenizer
model = VitsModel.from_pretrained("facebook/mms-tts-kor")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-kor")

# Initialize MetricsPersistence
metrics_persistence = MetricsPersistence()


# Example usage: Store a metric
def store_audio_metric(metric_name, value, labels=None):
    metrics_persistence.store_metric(metric_name, value, labels)


# Example usage: Retrieve metrics
def get_audio_metrics(metric_name, start_date=None, end_date=None):
    return metrics_persistence.get_metrics(metric_name, start_date, end_date)


@app.route("/api/process-questions/<video_id>", methods=["POST"])
def process_questions(video_id):
    """Process questions for a video, generating audio for each question."""
    try:
        data = request.json
        questions = data.get("questions", [])

        if not questions:
            return jsonify({"error": "No questions provided"}), 400

        generated_audio = []

        for question in questions:
            try:
                text = question["question_text"]
                inputs = tokenizer(text, return_tensors="pt")

                with torch.no_grad():
                    output = model(**inputs).waveform

                # Save the audio file
                output_path = os.path.join(
                    AUDIO_DIR, f"{video_id}_{question['id']}.wav"
                )
                scipy.io.wavfile.write(
                    output_path,
                    rate=model.config.sampling_rate,
                    data=output.numpy(),
                )

                AUDIO_GENERATED.inc()
                generated_audio.append(
                    {
                        "question_id": question["id"],
                        "audio_path": output_path,
                    }
                )

                # Store audio processing metric
                store_audio_metric(
                    "audio_processing_time",
                    1.23,
                    labels={"status": "success"},
                )

            except Exception as e:
                TTS_ERRORS.inc()
                logger.error(
                    f"Error generating audio for question {question['id']}: {e}"
                )

        return jsonify({"success": True, "generated_audio": generated_audio})

    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route("/api/audio/<filename>", methods=["GET"])
def get_audio(filename):
    """Retrieve an audio file."""
    try:
        filepath = os.path.join(AUDIO_DIR, filename)
        if not os.path.exists(filepath):
            return jsonify({"error": "Audio file not found"}), 404

        return send_file(
            filepath,
            mimetype="audio/wav",
            as_attachment=True,
            download_name=filename,
        )

    except Exception as e:
        logger.error(f"Error retrieving audio file {filename}: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
