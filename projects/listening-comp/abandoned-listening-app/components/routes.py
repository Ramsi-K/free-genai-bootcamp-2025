import os
import time
import logging
import sqlite3
import json
from flask import request, jsonify
from typing import Dict, Any
from . import models, database

logger = logging.getLogger(__name__)


def register_routes(app, db_path: str, audio_dir: str):
    @app.route("/api/process", methods=["POST"])
    def process_video():
        try:
            data = request.get_json()
            if not data or "url" not in data:
                return (
                    jsonify(
                        {
                            "error": "No URL provided",
                            "details": "Please provide a valid YouTube URL",
                        }
                    ),
                    400,
                )

            video_url = data["url"]
            level = data.get(
                "level", "intermediate"
            )  # Default to intermediate

            if level not in ["beginner", "intermediate", "advanced"]:
                return (
                    jsonify(
                        {
                            "error": "Invalid Level",
                            "details": "Level must be beginner, intermediate, or advanced",
                        }
                    ),
                    400,
                )

            # Validate URL format first
            try:
                video_id = models.extract_video_id(video_url)
            except ValueError as e:
                return (
                    jsonify(
                        {"error": "Invalid URL format", "details": str(e)}
                    ),
                    400,
                )

            # Get transcript with detailed error handling
            try:
                transcript = models.get_transcript(video_id)
            except Exception as e:
                error_msg = str(e)
                if "private" in error_msg.lower():
                    return (
                        jsonify(
                            {
                                "error": "Video Unavailable",
                                "details": "This video is private or unavailable",
                            }
                        ),
                        404,
                    )
                elif "disabled" in error_msg.lower():
                    return (
                        jsonify(
                            {
                                "error": "No Subtitles",
                                "details": "Subtitles are disabled for this video",
                            }
                        ),
                        400,
                    )
                elif "korean" in error_msg.lower():
                    return (
                        jsonify(
                            {
                                "error": "No Korean Subtitles",
                                "details": "This video doesn't have Korean subtitles",
                            }
                        ),
                        400,
                    )
                else:
                    return (
                        jsonify(
                            {"error": "Transcript Error", "details": str(e)}
                        ),
                        500,
                    )

            # Generate questions with specified level
            questions = models.generate_questions(
                transcript, num_questions=3, level=level
            )

            # Generate audio for each question
            for q in questions:
                audio_path = os.path.join(
                    audio_dir, f"{video_id}_{hash(q['question'])}.mp3"
                )
                q["audio_url"] = models.generate_audio(
                    q["question"], audio_path
                )

            # Save to database with level
            video_data = {
                "video_id": video_id,
                "title": "Video Title",  # TODO: Get from YouTube API
                "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/0.jpg",
                "processed_date": int(time.time()),
                "transcript": transcript,
                "metadata": str(questions),
                "difficulty_level": level,
            }
            database.save_video_data(db_path, video_data)

            # Save questions with level
            conn = sqlite3.connect(db_path)
            try:
                for q in questions:
                    conn.execute(
                        """
                        INSERT INTO questions 
                        (video_id, question, options, correct_answer, audio_path, difficulty_level)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            video_id,
                            q["question"],
                            json.dumps(q["options"]),
                            q["correct"],
                            q.get("audio_url", ""),
                            level,
                        ),
                    )
                conn.commit()
            finally:
                conn.close()

            return jsonify(
                {
                    "success": True,
                    "video_id": video_id,
                    "questions": questions,
                    "level": level,
                }
            )

        except Exception as e:
            logger.error(f"Processing error: {e}")
            return jsonify({"error": "Server Error", "details": str(e)}), 500

    @app.route("/api/videos/<video_id>")
    def get_video(video_id):
        try:
            data = database.get_video_data(db_path, video_id)
            if not data:
                return jsonify({"error": "Video not found"}), 404

            return jsonify(data)

        except Exception as e:
            logger.error(f"Error fetching video {video_id}: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/questions/<video_id>")
    def get_questions(video_id):
        """Get questions with difficulty level for a video."""
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get video data including level
            video = cursor.execute(
                "SELECT * FROM videos WHERE video_id = ?", (video_id,)
            ).fetchone()

            if not video:
                return (
                    jsonify({"success": False, "error": "Video not found"}),
                    404,
                )

            # Get questions
            questions = cursor.execute(
                "SELECT * FROM questions WHERE video_id = ?", (video_id,)
            ).fetchall()

            return jsonify(
                {
                    "success": True,
                    "video_title": video["title"],
                    "level": video.get("difficulty_level", "intermediate"),
                    "questions": [dict(q) for q in questions],
                }
            )

        except Exception as e:
            logger.error(f"Error fetching questions: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
        finally:
            conn.close()
