import os
import json
import time
import uuid
import logging
import tempfile
import numpy as np
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import soundfile as sf
from pydub import AudioSegment
import torch
import sqlite3
from prometheus_client import Counter, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from services.metrics.persistence import MetricsPersistence

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
CORS(app)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})

# Initialize Prometheus metrics
AUDIO_GENERATED = Counter(
    "audio_generated_total", "Total number of audio files generated"
)
TTS_ERRORS = Counter(
    "tts_errors_total", "Total number of errors during TTS generation"
)

# Add Prometheus metrics endpoint
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

# Initialize OpenTelemetry
OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
SERVICE_NAME_OTEL = os.getenv("SERVICE_NAME", "audio-module")

def init_telemetry():
    if not OTEL_EXPORTER_OTLP_ENDPOINT:
        logging.warning("OTEL_EXPORTER_OTLP_ENDPOINT not set. Telemetry disabled.")
        return
    try:
        resource = Resource(attributes={"service.name": SERVICE_NAME_OTEL})
        provider = TracerProvider(resource=resource)
        otlp_exporter = OTLPSpanExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT, insecure=True)
        span_processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(span_processor)
        trace.set_tracer_provider(provider)
        FlaskInstrumentor().instrument_app(app)
        logging.info(f"OpenTelemetry initialized for service: {SERVICE_NAME_OTEL}")
    except Exception as e:
        logging.error(f"Failed to initialize OpenTelemetry: {e}")

# Call telemetry initialization
init_telemetry()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
DATA_DIR = os.environ.get("DATA_DIR", "/shared/data")
USE_GPU = os.environ.get("USE_GPU", "false").lower() in ("true", "1", "yes")
TTS_MODEL = os.environ.get("TTS_MODEL")

if not TTS_MODEL:
    logger.error("TTS_MODEL environment variable not set")
    raise ValueError("TTS_MODEL must be set in environment variables")

# Database path and audio directory
DB_PATH = os.path.join(os.getcwd(), "..", "shared", "data", "app.db")
AUDIO_DIR = os.path.join(os.getcwd(), "..", "shared", "data", "audio")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# Check if GPU is available and should be used
if USE_GPU:
    if torch.cuda.is_available():
        DEVICE = torch.device("cuda")
        logger.info(
            f"Using GPU for audio processing: {torch.cuda.get_device_name(0)}"
        )
        logger.info(
            f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB"
        )
    else:
        DEVICE = torch.device("cpu")
        logger.warning(
            "USE_GPU=true but no GPU available, falling back to CPU"
        )
else:
    DEVICE = torch.device("cpu")
    logger.info("Using CPU for audio processing (USE_GPU=false)")

# Initialize TTS model
def initialize_tts_model():
    try:
        # Try to load MeloTTS for Korean TTS
        processor = AutoProcessor.from_pretrained(TTS_MODEL)
        model = AutoModel.from_pretrained(TTS_MODEL).to(DEVICE)
        return {"processor": processor, "model": model, "initialized": True}
    except Exception as e:
        logger.error(f"Failed to initialize TTS model: {e}")
        return {"initialized": False}

# Initialize the TTS model
tts_model = initialize_tts_model()

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
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("process_questions") as span:
        try:
            # Fetch questions from the database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, question_text, audio_segment FROM questions WHERE video_id = ?", (video_id,))
            questions = cursor.fetchall()
            conn.close()

            if not questions:
                return jsonify({"error": "No questions found for this video"}), 404

            generated_audio = []

            for question_id, question_text, audio_segment in questions:
                try:
                    # Generate audio for the question
                    input_text = f"{question_text}\n{audio_segment}"
                    inputs = tts_model["processor"].text_to_sequence(input_text)
                    audio = tts_model["model"].generate(inputs, sampling_rate=24000)

                    # Save the audio file
                    filename = f"{video_id}_{question_id}.wav"
                    filepath = os.path.join(AUDIO_DIR, filename)
                    sf.write(filepath, audio, 24000)

                    # Update the database with the audio file path
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE questions SET audio_path = ? WHERE id = ?", (filepath, question_id))
                    conn.commit()
                    conn.close()

                    AUDIO_GENERATED.inc()
                    generated_audio.append({"question_id": question_id, "audio_path": filepath})

                    # Store audio processing metric
                    store_audio_metric("audio_processing_time", 1.23, labels={"status": "success"})

                except Exception as e:
                    TTS_ERRORS.inc()
                    logger.error(f"Error generating audio for question {question_id}: {e}")

            return jsonify({"success": True, "generated_audio": generated_audio})

        except sqlite3.Error as e:
            span.record_exception(e)
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        except Exception as e:
            span.record_exception(e)
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
