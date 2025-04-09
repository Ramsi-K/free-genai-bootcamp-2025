import os
import sqlite3
import logging
import re
import json
import requests
import torch
import scipy.io.wavfile
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
)
from transformers import VitsModel, AutoTokenizer
from datetime import datetime
from prometheus_client import Counter, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --- Configuration ---
SHARED_DATA_DIR = os.path.join(os.getcwd(), "shared", "data")
DB_PATH = os.path.join(SHARED_DATA_DIR, "app.db")
AUDIO_DIR = os.path.join(SHARED_DATA_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3:8b")  # Default model if not set
TTS_MODEL_NAME = "facebook/mms-tts-kor"  # Using MMS TTS

# Initialize Flask app
app = Flask(__name__)
CORS(
    app, resources={r"/api/*": {"origins": "*"}}
)  # Allow all origins for API routes

# --- Prometheus Setup ---
TRANSCRIPTS_PROCESSED = Counter(
    "transcripts_processed_total",
    "Total number of transcripts successfully processed",
)
QUESTIONS_GENERATED = Counter(
    "questions_generated_total", "Total number of questions generated"
)
AUDIO_GENERATED = Counter(
    "audio_generated_total", "Total number of audio files generated"
)
PROCESSING_ERRORS = Counter(
    "processing_errors_total",
    "Total number of errors during processing",
    ["step"],
)

# Add Prometheus metrics endpoint
app.wsgi_app = DispatcherMiddleware(
    app.wsgi_app, {"/metrics": make_wsgi_app()}
)

# --- TTS Model Loading ---
try:
    logger.info(f"Loading TTS model: {TTS_MODEL_NAME}")
    tts_model = VitsModel.from_pretrained(TTS_MODEL_NAME)
    tts_tokenizer = AutoTokenizer.from_pretrained(TTS_MODEL_NAME)
    logger.info("TTS model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load TTS model: {e}", exc_info=True)
    tts_model = None
    tts_tokenizer = None


# --- Database Initialization ---
def init_shared_database():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # Videos table (simplified from transcript-processor)
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                title TEXT,
                author TEXT,
                length INTEGER,
                publish_date TEXT,
                views INTEGER,
                transcript TEXT,
                created_at TEXT
            )"""
            )
            # Segments table (simplified from transcript-processor)
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS segments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                start REAL,
                end REAL,
                duration REAL,
                text TEXT,
                FOREIGN KEY(video_id) REFERENCES videos(video_id)
            )"""
            )
            # Questions table (combined info, added audio_url)
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                question_text TEXT NOT NULL,
                choices TEXT NOT NULL, -- Store as JSON string
                correct_answer INTEGER NOT NULL, -- Store index 0-3
                audio_segment TEXT, -- Relevant transcript part
                audio_url TEXT, -- URL/path to the generated audio file
                created_at TEXT,
                FOREIGN KEY(video_id) REFERENCES videos(video_id)
            )"""
            )
        logger.info(
            f"Shared database initialized/verified successfully at {DB_PATH}"
        )
    except sqlite3.Error as e:
        logger.error(f"Failed to initialize shared database: {e}")
        raise  # Re-raise the exception to prevent app startup if DB fails


# --- Helper Functions ---


def extract_video_id(url):
    """Extract YouTube video ID from URL."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"(?:embed\/|v\/|youtu\.be\/)([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    logger.warning(f"Could not extract video ID from URL: {url}")
    return None


def parse_duration(duration_iso):
    """Parse ISO 8601 duration format to seconds."""
    if not duration_iso or not isinstance(duration_iso, str):
        return 0
    try:
        match = re.match(
            r"P(?:(?P<days>\d+)D)?T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>[\d.]+)S)?",
            duration_iso,
        )
        if not match:
            return 0
        parts = match.groupdict()
        time_in_seconds = (
            int(parts.get("days", 0) or 0) * 86400
            + int(parts.get("hours", 0) or 0) * 3600
            + int(parts.get("minutes", 0) or 0) * 60
            + float(parts.get("seconds", 0) or 0)
        )
        return int(time_in_seconds)
    except Exception as e:
        logger.error(f"Error parsing duration '{duration_iso}': {e}")
        return 0


def get_video_metadata(video_id):
    """Get video metadata using YouTube Data API (or fallback)."""
    if not YOUTUBE_API_KEY:
        logger.warning(
            f"No YouTube API Key provided for video {video_id}. Using fallback metadata."
        )
        return {
            "title": f"Video {video_id}",
            "author": "Unknown",
            "length": 0,
            "publish_date": None,
            "views": 0,
        }
    try:
        url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={YOUTUBE_API_KEY}&part=snippet,contentDetails,statistics"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data.get("items"):
            return None
        item = data["items"][0]
        snippet = item.get("snippet", {})
        content_details = item.get("contentDetails", {})
        statistics = item.get("statistics", {})
        duration_iso = content_details.get("duration")
        duration_seconds = parse_duration(duration_iso) if duration_iso else 0
        metadata = {
            "title": snippet.get("title", "Unknown Title"),
            "author": snippet.get("channelTitle", "Unknown Author"),
            "length": duration_seconds,
            "publish_date": snippet.get("publishedAt"),
            "views": int(statistics.get("viewCount", 0)),
        }
        logger.info(f"Successfully retrieved metadata for video {video_id}")
        return metadata
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error getting metadata for {video_id}: {e}")
        PROCESSING_ERRORS.labels(step="metadata_fetch").inc()
        return None
    except Exception as e:
        logger.error(
            f"Unexpected error getting metadata for {video_id}: {e}",
            exc_info=True,
        )
        PROCESSING_ERRORS.labels(step="metadata_fetch").inc()
        return None


def get_transcript(video_id):
    """Fetch Korean transcript for a YouTube video."""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_generated_transcript(["ko"])
        # Fetch the actual transcript data (list of dictionaries)
        transcript_data = transcript.fetch()
        # Format as plain text
        full_text = " ".join([entry["text"] for entry in transcript_data])
        # Prepare segments list
        segments = [
            {
                "start": entry["start"],
                "end": entry["start"] + entry["duration"],
                "duration": entry["duration"],
                "text": entry["text"],
            }
            for entry in transcript_data
        ]
        logger.info(f"Successfully fetched transcript for video {video_id}")
        TRANSCRIPTS_PROCESSED.inc()
        return full_text, segments
    except (NoTranscriptFound, TranscriptsDisabled) as e:
        logger.warning(
            f"Could not retrieve transcript for video {video_id}: {e}"
        )
        PROCESSING_ERRORS.labels(step="transcript_fetch").inc()
        return None, []
    except Exception as e:
        logger.error(
            f"Error fetching transcript for video {video_id}: {e}",
            exc_info=True,
        )
        PROCESSING_ERRORS.labels(step="transcript_fetch").inc()
        return None, []


def generate_questions_llm(transcript_text, num_questions=3):
    """Generate questions using Ollama LLM."""
    if not transcript_text:
        logger.warning("Cannot generate questions: transcript is empty.")
        return []
    try:
        prompt = (
            "You are an expert in creating TOPIK-style Korean language listening comprehension questions. "
            f"Based on the following transcript, generate exactly {num_questions} multiple-choice questions. "
            "Each question and its 4 answer choices must be in Korean. Indicate the correct answer index (0-3). "
            "Also, provide the relevant section of the transcript that corresponds to the question.\n\n"
            "The output MUST be a valid JSON object containing a single key 'questions' which is a list of question objects. "
            "Each question object must have the following keys: 'question_text' (string), 'choices' (list of 4 strings), 'correct_answer' (integer 0-3), 'audio_segment' (string).\n\n"
            "Example format:\n"
            "{\n"
            '  "questions": [\n'
            '    {"question_text": "질문 내용?", "choices": ["선택지1", "선택지2", "선택지3", "선택지4"], "correct_answer": 1, "audio_segment": "관련 대본 부분..."},\n'
            '    {"question_text": "다른 질문?", "choices": ["다른 선택지1", "다른 선택지2", "다른 선택지3", "다른 선택지4"], "correct_answer": 3, "audio_segment": "다른 관련 대본 부분..."}\n'
            "  ]\n"
            "}\n\n"
            f"Transcript:\n{transcript_text}"
        )

        logger.info(f"Sending request to Ollama: {OLLAMA_HOST}/api/generate")
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=120,
        )
        response.raise_for_status()
        response_text = response.text
        logger.debug(f"Raw Ollama response: {response_text}")

        try:
            result_json = json.loads(response_text)
            questions = result_json.get("questions", [])

            if not isinstance(questions, list):
                raise ValueError("LLM response 'questions' is not a list.")
            for q in questions:
                if not all(
                    k in q
                    for k in [
                        "question_text",
                        "choices",
                        "correct_answer",
                        "audio_segment",
                    ]
                ):
                    raise ValueError(
                        f"Question object missing required keys: {q}"
                    )
                if (
                    not isinstance(q["choices"], list)
                    or len(q["choices"]) != 4
                ):
                    raise ValueError(
                        f"Invalid 'choices' format in question: {q}"
                    )
                if not isinstance(q["correct_answer"], int) or not (
                    0 <= q["correct_answer"] <= 3
                ):
                    raise ValueError(
                        f"Invalid 'correct_answer' in question: {q}"
                    )

            logger.info(
                f"Successfully generated {len(questions)} questions from LLM."
            )
            QUESTIONS_GENERATED.inc(len(questions))
            return questions

        except json.JSONDecodeError as json_err:
            logger.error(
                f"Failed to decode JSON response from Ollama: {json_err}. Response text: {response_text}"
            )
            PROCESSING_ERRORS.labels(step="question_llm_json_decode").inc()
            return []
        except ValueError as val_err:
            logger.error(
                f"Invalid JSON structure received from Ollama: {val_err}. Response text: {response_text}"
            )
            PROCESSING_ERRORS.labels(step="question_llm_json_structure").inc()
            return []

    except requests.exceptions.Timeout:
        logger.error("Timeout calling Ollama LLM.")
        PROCESSING_ERRORS.labels(step="question_llm_timeout").inc()
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Ollama LLM: {e}")
        PROCESSING_ERRORS.labels(step="question_llm_request").inc()
        return []
    except Exception as e:
        logger.error(
            f"Unexpected error during question generation: {e}", exc_info=True
        )
        PROCESSING_ERRORS.labels(step="question_llm_other").inc()
        return []


def generate_tts_audio(text, filename_base):
    """Generate TTS audio using Hugging Face model and save to file."""
    if not tts_model or not tts_tokenizer:
        logger.error("TTS model not loaded. Cannot generate audio.")
        PROCESSING_ERRORS.labels(step="tts_model_load").inc()
        return None

    if not text or not isinstance(text, str) or not text.strip():
        logger.warning(
            f"Skipping TTS generation for empty text related to {filename_base}."
        )
        return None

    try:
        inputs = tts_tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            output = tts_model(**inputs).waveform
        waveform = output.squeeze().numpy()
        if waveform.ndim > 1:
            waveform = waveform[0]

        output_filename = f"{filename_base}.wav"
        output_path = os.path.join(AUDIO_DIR, output_filename)
        scipy.io.wavfile.write(
            output_path, rate=tts_model.config.sampling_rate, data=waveform
        )

        logger.info(f"Successfully generated audio file: {output_filename}")
        AUDIO_GENERATED.inc()
        return f"/api/audio/{output_filename}"
    except Exception as e:
        logger.error(
            f"Error generating TTS audio for '{filename_base}': {e}",
            exc_info=True,
        )
        PROCESSING_ERRORS.labels(step="tts_generation").inc()
        return None


def save_processed_data(
    video_id, metadata, transcript_text, segments, questions
):
    """Save all processed data to the database."""
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()

            cursor.execute(
                """
                INSERT OR REPLACE INTO videos (video_id, title, author, length, publish_date, views, transcript, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    video_id,
                    metadata.get("title"),
                    metadata.get("author"),
                    metadata.get("length"),
                    metadata.get("publish_date"),
                    metadata.get("views"),
                    transcript_text,
                    now,
                ),
            )

            cursor.execute(
                "DELETE FROM segments WHERE video_id = ?", (video_id,)
            )
            segment_data = [
                (
                    video_id,
                    seg["start"],
                    seg["end"],
                    seg["duration"],
                    seg["text"],
                )
                for seg in segments
            ]
            if segment_data:
                cursor.executemany(
                    """
                    INSERT INTO segments (video_id, start, end, duration, text) VALUES (?, ?, ?, ?, ?)
                """,
                    segment_data,
                )

            cursor.execute(
                "DELETE FROM questions WHERE video_id = ?", (video_id,)
            )
            question_data = [
                (
                    video_id,
                    q["question_text"],
                    json.dumps(q["choices"]),
                    q["correct_answer"],
                    q["audio_segment"],
                    q.get("audio_url"),
                    now,
                )
                for q in questions
            ]
            if question_data:
                cursor.executemany(
                    """
                    INSERT INTO questions (video_id, question_text, choices, correct_answer, audio_segment, audio_url, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    question_data,
                )

        logger.info(
            f"Successfully saved all data for video {video_id} to database."
        )
        return True
    except sqlite3.Error as e:
        logger.error(f"Database error saving data for video {video_id}: {e}")
        PROCESSING_ERRORS.labels(step="database_save").inc()
        return False
    except Exception as e:
        logger.error(
            f"Unexpected error saving data for video {video_id}: {e}",
            exc_info=True,
        )
        PROCESSING_ERRORS.labels(step="database_save").inc()
        return False


# --- API Endpoints ---


@app.route("/")
def home_route():
    return "Welcome to the Korean Listening Comprehension App API!", 200


@app.route("/health", methods=["GET"])
def health_check():
    db_ok = False
    try:
        with sqlite3.connect(DB_PATH, timeout=5) as conn:
            conn.cursor().execute("SELECT 1")
        db_ok = True
    except Exception as e:
        logger.error(f"Health check DB connection failed: {e}")

    tts_ok = tts_model is not None and tts_tokenizer is not None

    status = "healthy" if db_ok and tts_ok else "unhealthy"
    details = {
        "database_connection": "ok" if db_ok else "error",
        "tts_model_loaded": "ok" if tts_ok else "error",
    }

    if status == "healthy":
        return jsonify({"status": status, "details": details}), 200
    else:
        return jsonify({"status": status, "details": details}), 503


@app.route("/api/process", methods=["POST"])
def process_video_endpoint():
    data = request.json
    video_url = data.get("url")
    num_questions = data.get("num_questions", 3)

    if not video_url:
        return jsonify({"error": "Video URL is required"}), 400

    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    logger.info(f"Processing request for video ID: {video_id}")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM questions WHERE video_id = ?",
                (video_id,),
            )
            question_count = cursor.fetchone()[0]
            if question_count > 0:
                logger.info(
                    f"Video {video_id} already processed with questions. Skipping reprocessing."
                )
                return jsonify(
                    {
                        "success": True,
                        "video_id": video_id,
                        "message": "Video already processed",
                    }
                )
    except sqlite3.Error as e:
        logger.error(f"Database error checking existing video {video_id}: {e}")

    metadata = get_video_metadata(video_id)
    if not metadata:
        return jsonify({"error": "Failed to fetch video metadata"}), 500

    transcript_text, segments = get_transcript(video_id)
    if transcript_text is None:
        return (
            jsonify(
                {"error": "Failed to fetch or no Korean transcript found"}
            ),
            404,
        )

    questions = generate_questions_llm(transcript_text, num_questions)
    if not questions:
        return jsonify({"error": "Failed to generate questions from LLM"}), 500

    generated_questions_with_audio = []
    for i, q in enumerate(questions):
        question_text_for_tts = q.get("question_text", "")
        filename_base = f"{video_id}_q{i+1}"
        audio_url = generate_tts_audio(question_text_for_tts, filename_base)
        q_copy = q.copy()
        q_copy["audio_url"] = audio_url
        generated_questions_with_audio.append(q_copy)

    if not save_processed_data(
        video_id,
        metadata,
        transcript_text,
        segments,
        generated_questions_with_audio,
    ):
        return (
            jsonify({"error": "Failed to save processed data to database"}),
            500,
        )

    logger.info(f"Successfully processed video ID: {video_id}")
    return jsonify({"success": True, "video_id": video_id})


@app.route("/api/video/<video_id>", methods=["GET"])
def get_video_details(video_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM videos WHERE video_id = ?", (video_id,)
            )
            video_row = cursor.fetchone()

            if not video_row:
                return jsonify({"error": "Video not found"}), 404

            cursor.execute(
                "SELECT * FROM segments WHERE video_id = ? ORDER BY start",
                (video_id,),
            )
            segment_rows = cursor.fetchall()

            video_data = dict(video_row)
            segments_data = [dict(row) for row in segment_rows]

            return jsonify(
                {
                    "success": True,
                    "data": {
                        "metadata": video_data,
                        "segments": segments_data,
                    },
                }
            )

    except sqlite3.Error as e:
        logger.error(
            f"Database error fetching video details for {video_id}: {e}"
        )
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        logger.error(
            f"Unexpected error fetching video details for {video_id}: {e}",
            exc_info=True,
        )
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/questions/<video_id>", methods=["GET"])
def get_questions_for_video(video_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id, question_text, choices, correct_answer, audio_segment, audio_url
                FROM questions
                WHERE video_id = ?
                ORDER BY id
            """,
                (video_id,),
            )
            question_rows = cursor.fetchall()

            if not question_rows:
                return jsonify({"success": True, "questions": []})

            questions_data = []
            for row in question_rows:
                q_dict = dict(row)
                try:
                    q_dict["choices"] = json.loads(q_dict["choices"])
                except json.JSONDecodeError:
                    logger.warning(
                        f"Could not parse choices JSON for question {q_dict['id']}: {q_dict['choices']}"
                    )
                    q_dict["choices"] = []
                questions_data.append(q_dict)

            cursor.execute(
                "SELECT title FROM videos WHERE video_id = ?", (video_id,)
            )
            video_title_row = cursor.fetchone()
            video_title = (
                video_title_row["title"]
                if video_title_row
                else "Unknown Video"
            )

            return jsonify(
                {
                    "success": True,
                    "video_title": video_title,
                    "questions": questions_data,
                }
            )

    except sqlite3.Error as e:
        logger.error(f"Database error fetching questions for {video_id}: {e}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        logger.error(
            f"Unexpected error fetching questions for {video_id}: {e}",
            exc_info=True,
        )
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/audio/<filename>", methods=["GET"])
def serve_audio_file(filename):
    logger.debug(
        f"Attempting to serve audio file: {filename} from {AUDIO_DIR}"
    )
    if ".." in filename or filename.startswith("/"):
        return jsonify({"error": "Invalid filename"}), 400
    try:
        return send_from_directory(AUDIO_DIR, filename, mimetype="audio/wav")
    except FileNotFoundError:
        logger.warning(f"Audio file not found: {filename}")
        return jsonify({"error": "Audio file not found"}), 404
    except Exception as e:
        logger.error(
            f"Error serving audio file {filename}: {e}", exc_info=True
        )
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    init_shared_database()
    logger.info("Starting Flask app on port 8000...")
    app.run(
        host="0.0.0.0", port=8000, debug=os.environ.get("FLASK_DEBUG", False)
    )
