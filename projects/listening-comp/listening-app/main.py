import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@app.route("/api/transcript", methods=["GET"])
def get_transcript():
    video_id = request.args.get("video_id")
    if not video_id:
        return jsonify({"error": "Missing video_id parameter"}), 400

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([item["text"] for item in transcript])
        return jsonify({"transcript": transcript_text})
    except TranscriptsDisabled:
        logger.error(f"Subtitles are disabled for video {video_id}")
        return (
            jsonify({"error": "Subtitles are disabled for this video."}),
            404,
        )
    except Exception as e:
        logger.error(f"Error retrieving transcript for video {video_id}: {e}")
        return jsonify({"error": "Failed to retrieve transcript."}), 500


@app.route("/api/questions", methods=["POST"])
def generate_questions():
    data = request.get_json()
    transcript = data.get("transcript")

    if not transcript:
        return jsonify({"error": "Missing transcript in request body"}), 400

    try:
        # Placeholder for LLM question generation logic
        questions = [
            {
                "question": "What is the main topic?",
                "options": ["A", "B", "C", "D"],
                "answer": "A",
            }
        ]
        return jsonify({"questions": questions})
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        return jsonify({"error": "Failed to generate questions."}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
