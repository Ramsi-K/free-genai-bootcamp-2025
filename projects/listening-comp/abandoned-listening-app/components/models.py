import os
import json
import requests
import logging
import re
from typing import List, Dict
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

logger = logging.getLogger(__name__)


def check_ollama_model() -> bool:
    """Check if required LLM model is available."""
    try:
        response = requests.get("http://ollama:11434/api/tags")
        models = response.json().get("models", [])
        model_name = os.getenv("LLM_MODEL", "exaone3.5:2.4b")
        return any(m["name"] == model_name for m in models)
    except Exception as e:
        logger.error(f"Failed to check Ollama model: {e}")
        return False


def init_tts_model() -> None:
    """Initialize TTS model (placeholder for actual implementation)."""
    pass


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([^"&?/\s]{11})',  # Standard & shortened
        r'(?:shorts/)([^"&?/\s]{11})',  # Shorts format
    ]

    for pattern in patterns:
        if match := re.search(pattern, url):
            return match.group(1)
    raise ValueError("Invalid YouTube URL format")


def get_transcript(video_id: str) -> str:
    """Get and validate Korean transcript from YouTube."""
    try:
        # Clean video ID from URL if full URL was passed
        if "youtube.com" in video_id or "youtu.be" in video_id:
            video_id = extract_video_id(video_id)

        # Try different Korean subtitle variants with fallbacks
        errors = []
        for lang in ["ko", "ko-KR"]:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(
                    video_id, languages=[lang]
                )
                return " ".join(t["text"] for t in transcript)
            except NoTranscriptFound as e:
                errors.append(f"No {lang} subtitles found")
                continue
            except TranscriptsDisabled as e:
                raise Exception("Subtitles are disabled for this video")
            except VideoUnavailable as e:
                raise Exception("Video is private or unavailable")

        # If we get here, no Korean subtitles were found
        error_msg = " and ".join(errors)
        raise Exception(f"No Korean subtitles available: {error_msg}")

    except Exception as e:
        logger.error(f"Failed to get transcript for video {video_id}: {e}")
        raise


def generate_questions(
    transcript: str, num_questions: int = 3, level: str = "intermediate"
) -> List[Dict]:
    """Generate TOPIK-style listening comprehension questions."""

    # TOPIK question patterns based on level
    patterns = {
        "beginner": [
            "주제를 고르십시오.",  # Choose the topic
            "들은 내용과 같은 것을 고르십시오.",  # Choose what matches what you heard
            "무엇에 대한 이야기입니까?",  # What is this talk about?
        ],
        "intermediate": [
            "들은 내용과 일치하는 것을 고르십시오.",  # Choose what matches the content
            "이야기를 듣고 물음에 답하십시오.",  # Listen to the story and answer the question
            "대화 내용과 일치하는 것을 고르십시오.",  # Choose what matches the conversation
        ],
        "advanced": [
            "들은 내용의 중심 생각을 고르십시오.",  # Choose the main idea
            "들은 내용을 바탕으로 할 때, 대화의 의도로 알맞은 것을 고르십시오.",  # Based on what you heard, choose the appropriate intention
            "이어질 내용으로 가장 알맞은 것을 고르십시오.",  # Choose the most appropriate continuation
        ],
    }

    # Format prompt with specific TOPIK patterns and examples
    prompt = f"""
    Generate {num_questions} TOPIK-style listening comprehension questions in Korean for this transcript.
    Use these exact TOPIK patterns: {patterns[level]}
    
    Each question must:
    1. Follow official TOPIK listening format
    2. Include 4 options (가, 나, 다, 라)
    3. Have clear distractors based on transcript content
    4. Match {level} difficulty level
    
    Format as JSON array:
    [{{
        "question": "Question text (using TOPIK pattern)",
        "options": ["가. option1", "나. option2", "다. option3", "라. option4"],
        "correct": 0,  // index of correct answer
        "pattern": "TOPIK pattern used"
    }}]
    
    Transcript: {transcript[:1000]}...
    """

    try:
        response = requests.post(
            "http://ollama:11434/api/generate",
            json={
                "model": os.getenv("LLM_MODEL", "exaone3.5:2.4b"),
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "top_p": 0.9},
            },
        )

        result = response.json()["response"]
        # Extract JSON from response
        json_str = result[result.find("[") : result.rfind("]") + 1]
        questions = json.loads(json_str)

        # Validate question format
        for q in questions:
            if not all(
                k in q for k in ["question", "options", "correct", "pattern"]
            ):
                raise ValueError("Invalid question format from LLM")
            if len(q["options"]) != 4:
                raise ValueError("Each question must have exactly 4 options")
            if not 0 <= q["correct"] < 4:
                raise ValueError("Invalid correct answer index")

        return questions

    except Exception as e:
        logger.error(f"Failed to generate TOPIK questions: {e}")
        raise


def generate_audio(text: str, output_path: str) -> str:
    """Generate TTS audio for question (placeholder)."""
    # TODO: Implement actual TTS
    logger.info(f"Would generate audio for: {text}")
    return output_path
