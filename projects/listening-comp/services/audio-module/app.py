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
import asyncio
from transformers import AutoProcessor, AutoModel
from functools import wraps  # Add explicit import for wraps

# Import OPEA components
from comps import (
    MicroService,
    ServiceOrchestrator,
    ServiceType,
    ServiceRoleType,
)
from comps.cores.proto.api_protocol import (
    TTSRequest,
    TTSResponse,
    ServiceException,
)
import asyncio
from flask import Flask, request, jsonify
from flask.helpers import make_response
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from wrappers import ServiceWrapper, init_telemetry, AUDIO_GENERATED


# Define async handler for Flask to work with async functions
def async_handler(f):
    @wraps(f)
    def inner(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        result = loop.run_until_complete(f(*args, **kwargs))
        # Close the loop if it was created in this function
        if not loop.is_running():
            loop.close()
        return result

    return inner


# Initialize OTEL
trace.set_tracer_provider(TracerProvider())
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
CORS(app)

# Initialize telemetry
init_telemetry(port=8002)
wrapper = ServiceWrapper("audio_module")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
DATA_DIR = os.environ.get("DATA_DIR", "/shared/data")
AUDIO_DIR = os.environ.get("AUDIO_DIR", "/shared/data/audio")
USE_GPU = os.environ.get("USE_GPU", "false").lower() in ("true", "1", "yes")
TTS_MODEL = os.environ.get("TTS_MODEL")

if not TTS_MODEL:
    logger.error("TTS_MODEL environment variable not set")
    raise ValueError("TTS_MODEL must be set in environment variables")

# Create directories
os.makedirs(DATA_DIR, exist_ok=True)
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

# Initialize ServiceOrchestrator without device parameter
service_orchestrator = ServiceOrchestrator()

# Define TTS service
tts_service = MicroService(
    name="tts_service",
    service_type=ServiceType.PROCESSOR,
    host="0.0.0.0",
    port=5002,
    endpoint="/api/tts",
    use_remote_service=False,
    config={"model": TTS_MODEL, "sample_rate": 24000},
)

service_orchestrator.add(tts_service)


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


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


# Add proper service exception handling
def safe_tts_operation(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"TTS operation failed: {str(e)}")
            raise ServiceException(f"TTS service error: {str(e)}")

    return wrapper


@app.route("/api/tts", methods=["POST"])
@wrapper.endpoint_handler("text_to_speech")
@safe_tts_operation
async def text_to_speech():
    """Convert text to speech using OPEA components."""
    try:
        data = request.json
        if not data or "text" not in data:
            raise ServiceException("Text is required")

        text = data["text"]
        voice = data.get("voice", "default")

        if not tts_model["initialized"]:
            raise ServiceException("TTS model not initialized")

        # Create OPEA TTSRequest
        tts_request = TTSRequest(text=text, voice=voice)

        # Process through service orchestrator
        result_dict, runtime_graph = await service_orchestrator.schedule(
            initial_inputs={"request": tts_request},
            model_parameters={"device": DEVICE},
        )

        # Get result from last node
        last_node = runtime_graph.all_leaves()[-1]
        audio_data = result_dict[last_node]

        filename = f"{uuid.uuid4()}.wav"
        filepath = os.path.join(AUDIO_DIR, filename)

        # Save the audio file
        sf.write(filepath, audio_data.audio_values, audio_data.sample_rate)

        AUDIO_GENERATED.inc()
        return TTSResponse(
            success=True,
            audio_path=filepath,
            audio_url=f"/api/audio/{filename}",
        ).dict()

    except ServiceException as e:
        logger.error(f"Service error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"System error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/process-questions/<video_id>", methods=["POST"])
async def process_questions(video_id):
    """Process questions for a video, generating audio for each question."""
    try:
        # Get questions file
        questions_path = os.path.join(DATA_DIR, f"{video_id}_questions.json")
        if not os.path.exists(questions_path):
            return jsonify({"error": "No questions found for this video"}), 404

        with open(questions_path, "r", encoding="utf-8") as f:
            questions_data = json.load(f)

        questions = questions_data.get("questions", [])
        if not questions:
            return jsonify({"error": "No questions found in the data"}), 400

        # Process each question using OPEA TTS service
        for i, question in enumerate(questions):
            # Generate audio for the question
            question_text = question.get("question", "")
            if question_text:
                try:
                    # Create TTS request
                    tts_request = {"text": question_text, "voice": "default"}

                    # Call our own TTS endpoint
                    tts_response = await text_to_speech()
                    if tts_response.status_code == 200:
                        tts_data = tts_response.get_json()
                        if tts_data.get("success"):
                            # Add audio information to the question
                            questions[i]["audio_url"] = tts_data.get(
                                "audio_url"
                            )
                except Exception as e:
                    logger.error(
                        f"Error generating audio for question {i}: {e}"
                    )

        # Update questions file with audio URLs
        questions_data["questions"] = questions
        with open(questions_path, "w", encoding="utf-8") as f:
            json.dump(questions_data, f, ensure_ascii=False, indent=2)

        return jsonify(
            {
                "success": True,
                "message": f"Processed {len(questions)} questions with audio",
                "questions": questions,
            }
        )

    except Exception as e:
        logger.error(f"Error processing questions for video {video_id}: {e}")
        return jsonify({"error": str(e)}), 500


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


@app.route("/api/extract-audio/<video_id>", methods=["POST"])
def extract_audio_segment(video_id):
    """Extract audio segment from a video."""
    try:
        data = request.json
        if not data or "start" not in data or "end" not in data:
            return jsonify({"error": "Start and end times are required"}), 400

        start_time = float(data["start"])
        end_time = float(data["end"])

        # Check if we have the full audio file
        audio_file = os.path.join(AUDIO_DIR, f"{video_id}_full.wav")

        if not os.path.exists(audio_file):
            # If we don't have the audio, check if we can get it from the transcript metadata
            file_path = os.path.join(DATA_DIR, f"{video_id}.json")
            if not os.path.exists(file_path):
                return jsonify({"error": "Video data not found"}), 404

            # This would normally download the audio from YouTube or another source
            # For this example, we'll return an error as we don't have the audio
            return (
                jsonify({"error": "Full audio not available for this video"}),
                400,
            )

        # Load audio file
        audio = AudioSegment.from_wav(audio_file)

        # Convert start and end times to milliseconds
        start_ms = int(start_time * 1000)
        end_ms = int(end_time * 1000)

        # Extract segment
        segment = audio[start_ms:end_ms]

        # Create a unique filename
        segment_filename = f"{video_id}_{start_ms}_{end_ms}.wav"
        segment_filepath = os.path.join(AUDIO_DIR, segment_filename)

        # Export segment
        segment.export(segment_filepath, format="wav")

        return jsonify(
            {
                "success": True,
                "audio_path": segment_filepath,
                "audio_url": f"/api/audio/{segment_filename}",
            }
        )

    except Exception as e:
        logger.error(f"Error extracting audio segment: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/audio-questions/<video_id>", methods=["GET"])
def get_audio_questions(video_id):
    """Get questions with audio URLs for a video."""
    try:
        questions_path = os.path.join(DATA_DIR, f"{video_id}_questions.json")
        if not os.path.exists(questions_path):
            return jsonify({"error": "No questions found for this video"}), 404

        with open(questions_path, "r", encoding="utf-8") as f:
            questions_data = json.load(f)

        # Filter questions to include only those with audio
        questions = questions_data.get("questions", [])
        audio_questions = [q for q in questions if "audio_url" in q]

        return jsonify(
            {
                "success": True,
                "questions": audio_questions,
                "count": len(audio_questions),
            }
        )

    except Exception as e:
        logger.error(
            f"Error getting audio questions for video {video_id}: {e}"
        )
        return jsonify({"error": str(e)}), 500


# Fallback method for TTS if transformers model is not available
def fallback_tts(text):
    """Fallback method for TTS using an external service."""
    try:
        # Use an external API or default sound file
        filename = f"{uuid.uuid4()}.wav"
        filepath = os.path.join(AUDIO_DIR, "fallback.wav")

        # For demo purposes, we'll create a simple sine wave
        sample_rate = 24000
        duration = 2.0  # seconds
        t = np.linspace(
            0, duration, int(sample_rate * duration), endpoint=False
        )
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave

        # Save to file
        sf.write(filepath, audio, sample_rate)

        return {
            "success": True,
            "audio_path": filepath,
            "audio_url": f"/api/audio/fallback.wav",
        }
    except Exception as e:
        logger.error(f"Error in fallback TTS: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Register routes with service orchestrator
    service_orchestrator.register_routes(
        [
            ("/api/tts", text_to_speech, ["POST"]),
            ("/api/process-questions/<video_id>", process_questions, ["POST"]),
            ("/api/audio/<filename>", get_audio, ["GET"]),
            ("/api/extract-audio/<video_id>", extract_audio_segment, ["POST"]),
        ]
    )

    # Start the OPEA MicroService
    service_orchestrator.start()
    app.run(host="0.0.0.0", port=5002)
