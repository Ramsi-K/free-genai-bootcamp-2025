import os
import sqlite3
import logging
from flask import Flask, request, jsonify
import importlib

transcript_processor = importlib.import_module("services.transcript-processor")
question_module = importlib.import_module("services.question-module")
audio_module = importlib.import_module("services.audio-module")


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Shared database path
DB_PATH = os.path.join(os.getcwd(), "shared", "data", "app.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Initialize Flask app
app = Flask(__name__)


# Initialize the shared database
def init_shared_database():
    """Initialize the shared SQLite database with required tables."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create transcripts table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transcripts (
                video_id TEXT PRIMARY KEY,
                transcript_text TEXT NOT NULL,
                metadata TEXT
            )
            """
        )

        # Create questions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                question_text TEXT NOT NULL,
                choices TEXT NOT NULL,
                correct_answer INTEGER NOT NULL,
                audio_segment TEXT NOT NULL,
                FOREIGN KEY(video_id) REFERENCES transcripts(video_id)
            )
            """
        )

        # Create audio table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                audio_path TEXT NOT NULL,
                FOREIGN KEY(video_id) REFERENCES transcripts(video_id)
            )
            """
        )

        conn.commit()
        conn.close()
        logger.info(f"Shared database initialized successfully at {DB_PATH}")
    except sqlite3.Error as e:
        logger.error(f"Failed to initialize shared database: {e}")


@app.route("/api/process", methods=["POST"])
def process_video():
    """Process a video through the pipeline: Transcript → Questions → Audio."""
    data = request.json
    video_url = data.get("url")
    num_questions = data.get("num_questions", 3)

    if not video_url:
        return jsonify({"error": "Video URL is required"}), 400

    try:
        # Step 1: Process transcript
        transcript_result = transcript_processor.process_transcript(video_url)

        # Step 2: Generate questions
        questions_result = question_module.generate_questions(
            transcript=transcript_result["transcript_text"],
            video_id=transcript_result["video_id"],
            num_questions=num_questions,
        )

        # Step 3: Generate audio for questions
        audio_results = []
        for question in questions_result:
            audio_result = audio_module.generate_audio(
                text=question["question_text"],
                video_id=transcript_result["video_id"],
                question_id=question["id"],
            )
            audio_results.append(audio_result)

        return jsonify(
            {
                "success": True,
                "transcript": transcript_result,
                "questions": questions_result,
                "audio_files": audio_results,
            }
        )

    except Exception as e:
        logger.error(f"Error processing video: {e}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    init_shared_database()
    app.run(host="0.0.0.0", port=8000)
