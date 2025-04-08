import os
import logging
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from prometheus_client import Counter, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import time

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Prometheus metrics
QUESTIONS_GENERATED = Counter(
    "questions_generated_total", "Total number of questions generated"
)
LLM_ERRORS = Counter(
    "llm_errors_total", "Total number of errors during LLM calls"
)

# Add Prometheus metrics endpoint
app.wsgi_app = DispatcherMiddleware(
    app.wsgi_app, {"/metrics": make_wsgi_app()}
)

# Database path
DB_PATH = os.path.join(os.getcwd(), "..", "shared", "data", "app.db")

# Ollama LLM endpoint
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")


@app.route("/api/generate-questions", methods=["POST"])
def generate_questions():
    """Generate TOPIK-style questions from a transcript."""
    data = request.json
    transcript = data.get("transcript")
    video_id = data.get("video_id")
    num_questions = data.get("num_questions", 3)

    if not transcript or not video_id:
        return (
            jsonify({"error": "Transcript and video_id are required"}),
            400,
        )

    try:
        # Define the stronger prompt for the LLM
        prompt = (
            "You are an expert in creating TOPIK-style Korean language listening comprehension questions. "
            "Based on the following transcript, generate {num_questions} multiple-choice questions. "
            "Each question and its answer choices must be in Korean. Indicate the correct answer. "
            "Also, provide the relevant section of the transcript that corresponds to the question.\n\n"
            "The output must be in the following JSON format:\n"
            '{"questions": [\n'
            '  {"question_text": "<question text in Korean>", "choices": ["<choice1 in Korean>", "<choice2 in Korean>", "<choice3 in Korean>", "<choice4 in Korean>"], "correct_answer": <index of correct answer (0-3)>, "audio_segment": "<relevant transcript section>"}\n'
            "]}\n\n"
            f"Transcript:\n{transcript}"
        )

        # Call Ollama LLM to generate questions
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"prompt": prompt, "no-stream": True},
        )
        response.raise_for_status()
        questions = response.json().get("questions", [])

        # Increment Prometheus counter
        QUESTIONS_GENERATED.inc(len(questions))

        # Store questions in the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for question in questions:
            cursor.execute(
                """
                INSERT INTO questions (video_id, question_text, choices, correct_answer, audio_segment)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    video_id,
                    question["question_text"],
                    json.dumps(question["choices"]),
                    question["correct_answer"],
                    question["audio_segment"],
                ),
            )
        conn.commit()
        conn.close()

        return jsonify({"success": True, "questions": questions})

    except requests.exceptions.RequestException as e:
        LLM_ERRORS.inc()
        return jsonify({"error": f"LLM request failed: {str(e)}"}), 500
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})


@app.route("/")
def home():
    return "Welcome to the Question Generator API!", 200
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
