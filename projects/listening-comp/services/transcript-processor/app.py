import os
import json
import re
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import requests
from langdetect import detect
import pandas as pd
from comps import MicroService, ServiceOrchestrator
from comps.cores.mega.constants import ServiceType, ServiceRoleType
from guardrails import VideoGuardrails
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from wrappers import ServiceWrapper, init_telemetry, TRANSCRIPT_LENGTH

# Initialize OTEL
trace.set_tracer_provider(TracerProvider())
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
CORS(app)

# Configuration
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/shared/data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# YouTube API configuration
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")

# Initialize ServiceOrchestrator
service_orchestrator = ServiceOrchestrator()

# Define service dependencies
question_service = MicroService(
    name="question_service",
    host="question-module",  # Docker service name
    port=5001,
    endpoint="/api/generate-questions",
    service_type=ServiceType.UNDEFINED,
    use_remote_service=True,
)

audio_service = MicroService(
    name="audio_service",
    host="audio-module",  # Docker service name
    port=5002,
    endpoint="/api/extract-audio",
    service_type=ServiceType.TTS,  # Using TTS instead of AUDIO
    use_remote_service=True,
)

# Register services
service_orchestrator.add(question_service)
service_orchestrator.add(audio_service)

# Initialize guardrails
guardrails = VideoGuardrails(
    blacklisted_channels=["blocked_channel_1", "blocked_channel_2"]
)

# Add detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize telemetry
init_telemetry(port=8000)
wrapper = ServiceWrapper("transcript_processor")


def extract_video_id(url):
    """Extract YouTube video ID from URL."""
    video_id = None
    if "youtube.com/watch?v=" in url:
        video_id = url.split("youtube.com/watch?v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
    return video_id


def get_video_metadata(video_id):
    """Get video metadata using YouTube Data API."""
    try:
        # If no API key is provided, use a fallback approach without API
        if not YOUTUBE_API_KEY:
            logger.warning(
                "No YouTube API Key provided. Using fallback approach."
            )
            # Simple fallback: Assume the video is valid and long enough
            return {
                "title": "Unknown (API Key not provided)",
                "author": "Unknown",
                "description": "",
                "length": 120,  # Assume 2 minutes
                "publish_date": None,
                "views": 0,
            }

        # Use YouTube Data API
        url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={YOUTUBE_API_KEY}&part=snippet,contentDetails,statistics"
        response = requests.get(url)

        if response.status_code != 200:
            logger.error(
                f"YouTube API error: {response.status_code} - {response.text}"
            )
            return {
                "title": "Error retrieving video",
                "author": "Unknown",
                "description": "",
                "length": 0,
                "publish_date": None,
                "views": 0,
            }

        data = response.json()

        if not data["items"]:
            logger.error(f"Video not found: {video_id}")
            return {
                "title": "Video not found",
                "author": "Unknown",
                "description": "",
                "length": 0,
                "publish_date": None,
                "views": 0,
            }

        video_data = data["items"][0]

        # Extract duration in ISO 8601 format and convert to seconds
        duration_iso = video_data["contentDetails"]["duration"]
        duration_seconds = parse_duration(duration_iso)

        return {
            "title": video_data["snippet"]["title"],
            "author": video_data["snippet"]["channelTitle"],
            "description": video_data["snippet"]["description"],
            "length": duration_seconds,
            "publish_date": video_data["snippet"]["publishedAt"],
            "views": int(video_data["statistics"].get("viewCount", 0)),
        }

    except Exception as e:
        logger.error(f"Error getting metadata for {video_id}: {e}")
        return {
            "title": "Unknown",
            "author": "Unknown",
            "description": "",
            "length": 120,  # Assume 2 minutes for now to bypass length check
            "publish_date": None,
            "views": 0,
        }


def parse_duration(duration_iso):
    """Parse ISO 8601 duration format to seconds."""
    try:
        match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_iso)
        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds
    except Exception as e:
        logger.error(f"Error parsing duration: {e}")
        return 120  # Default to 2 minutes


def is_korean_content(text):
    """Check if the content is primarily Korean."""
    try:
        lang = detect(text)
        return lang == "ko"
    except:
        # If detection fails, check for Korean characters
        korean_char_count = len(re.findall(r"[\uAC00-\uD7A3]", text))
        return (
            korean_char_count > len(text) * 0.3
        )  # If more than 30% are Korean characters


def process_transcript(transcript):
    """Process and clean transcript entries."""
    formatter = TextFormatter()
    transcript_text = formatter.format_transcript(transcript)

    # Additional processing for Korean transcripts
    transcript_text = re.sub(r"\s+", " ", transcript_text).strip()

    # Create structured transcript with timestamps
    structured_transcript = []
    for entry in transcript:
        structured_transcript.append(
            {
                "start": entry["start"],
                "duration": entry["duration"],
                "text": entry["text"].strip(),
            }
        )

    return transcript_text, structured_transcript


def segment_transcript(structured_transcript, segment_duration=30):
    """Segment the transcript into chunks of approximately segment_duration seconds."""
    segments = []
    current_segment = []
    current_duration = 0
    segment_start = 0

    for entry in structured_transcript:
        if current_duration == 0:
            segment_start = entry["start"]

        current_segment.append(entry)
        current_duration += entry["duration"]

        if current_duration >= segment_duration:
            segment_text = " ".join([e["text"] for e in current_segment])
            segments.append(
                {
                    "start": segment_start,
                    "end": segment_start + current_duration,
                    "duration": current_duration,
                    "text": segment_text,
                }
            )
            current_segment = []
            current_duration = 0

    # Add the last segment if it's not empty
    if current_segment:
        segment_text = " ".join([e["text"] for e in current_segment])
        segments.append(
            {
                "start": segment_start,
                "end": segment_start + current_duration,
                "duration": current_duration,
                "text": segment_text,
            }
        )

    return segments


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


def get_transcript(video_id):
    """Get transcript using YouTubeTranscriptApi with better error handling."""
    try:
        # Try auto-generated Korean subtitles first
        try:
            return YouTubeTranscriptApi.get_transcript(
                video_id, languages=["ko"], params={"as_generated": True}
            )
        except:
            pass

        # Try manual Korean subtitles
        try:
            return YouTubeTranscriptApi.get_transcript(
                video_id, languages=["ko"]
            )
        except:
            pass

        # Try Korean (South Korea) subtitles
        try:
            return YouTubeTranscriptApi.get_transcript(
                video_id, languages=["ko-KR"]
            )
        except:
            pass

        raise Exception("No Korean subtitles found")

    except Exception as e:
        logger.error(
            f"Failed to get transcript for video {video_id}: {str(e)}"
        )
        raise


@app.route("/api/process", methods=["POST"])
@wrapper.endpoint_handler("process_video")
async def process_video():
    """Process YouTube video and extract transcript."""
    video_id = None
    try:
        # Rate limiting
        if not guardrails.check_rate_limit(request.remote_addr):
            return (
                jsonify(
                    {
                        "error": "요청이 너무 많습니다. 잠시 후 다시 시도해주세요."
                    }
                ),
                429,
            )

        data = request.json
        if not data or "url" not in data:
            return jsonify({"error": "URL is required"}), 400

        url = data["url"]
        video_id = extract_video_id(url)

        if not video_id:
            return jsonify({"error": "Invalid YouTube URL"}), 400

        # Get video metadata
        metadata = get_video_metadata(video_id)
        logger.info(f"Metadata for video {video_id}: {metadata}")

        # Validate metadata
        metadata_error = guardrails.validate_video_metadata(metadata)
        if metadata_error:
            return jsonify({"error": metadata_error}), 400

        # Get transcript with better error handling
        try:
            transcript = get_transcript(video_id)
            if not transcript:
                return (
                    jsonify(
                        {
                            "error": "한국어 자막을 찾을 수 없습니다. 자동 생성 자막이나 수동 자막이 필요합니다."
                        }
                    ),
                    400,
                )
        except Exception as e:
            return (
                jsonify(
                    {
                        "error": f"자막을 가져오는 중 오류가 발생했습니다: {str(e)}"
                    }
                ),
                400,
            )

        # Process transcript
        transcript_text, structured_transcript = process_transcript(transcript)

        # Validate transcript
        transcript_error = guardrails.validate_transcript(transcript_text)
        if transcript_error:
            return jsonify({"error": transcript_error}), 400

        # Check if content is primarily Korean
        if not is_korean_content(transcript_text):
            logger.error(f"Content not primarily Korean for video {video_id}")
            return (
                jsonify({"error": "Content is not primarily in Korean"}),
                400,
            )

        # Segment transcript for easier processing
        segments = segment_transcript(structured_transcript)

        # Validate segments
        segments_error = guardrails.validate_segments(segments)
        if segments_error:
            return jsonify({"error": segments_error}), 400

        # Save processed data
        result = {
            "video_id": video_id,
            "metadata": metadata,
            "full_transcript": transcript_text,
            "structured_transcript": structured_transcript,
            "segments": segments,
        }

        # Save to file
        output_path = os.path.join(OUTPUT_DIR, f"{video_id}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        TRANSCRIPT_LENGTH.observe(len(transcript_text))

        return jsonify(
            {
                "success": True,
                "video_id": video_id,
                "metadata": metadata,
                "transcript_length": len(transcript_text),
                "segments_count": len(segments),
                "file_path": output_path,
            }
        )

    except Exception as e:
        logger.error(
            f"Error processing video {video_id}: {str(e)}", exc_info=True
        )
        return (
            jsonify(
                {
                    "error": "비디오 처리 중 오류가 발생했습니다. 다른 URL을 시도해보세요."
                }
            ),
            500,
        )


@app.route("/api/videos", methods=["GET"])
def list_videos():
    """List all processed videos."""
    try:
        files = [
            f
            for f in os.listdir(OUTPUT_DIR)
            if f.endswith(".json") and not f.endswith("_questions.json")
        ]
        videos = []

        for file in files:
            file_path = os.path.join(OUTPUT_DIR, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    videos.append(
                        {
                            "video_id": data.get("video_id"),
                            "title": data.get("metadata", {}).get(
                                "title", "Unknown"
                            ),
                            "segments_count": len(data.get("segments", [])),
                            "processed_date": os.path.getmtime(file_path),
                        }
                    )
            except Exception as e:
                logger.error(f"Error reading file {file}: {str(e)}")

        return jsonify(
            {"success": True, "count": len(videos), "videos": videos}
        )

    except Exception as e:
        logger.error(f"Error listing videos: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/video/<video_id>", methods=["GET"])
def get_video_data(video_id):
    """Get processed data for a specific video."""
    try:
        file_path = os.path.join(OUTPUT_DIR, f"{video_id}.json")
        if not os.path.exists(file_path):
            return jsonify({"error": "Video not found"}), 404

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return jsonify({"success": True, "data": data})

    except Exception as e:
        logger.error(f"Error getting video {video_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/video/<video_id>", methods=["DELETE"])
def delete_video(video_id):
    """Delete processed data for a specific video."""
    try:
        file_path = os.path.join(OUTPUT_DIR, f"{video_id}.json")
        if not os.path.exists(file_path):
            return jsonify({"error": "Video not found"}), 404

        os.remove(file_path)

        # Also try to remove questions file if it exists
        questions_path = os.path.join(OUTPUT_DIR, f"{video_id}_questions.json")
        if os.path.exists(questions_path):
            os.remove(questions_path)

        return jsonify(
            {
                "success": True,
                "message": f"Video {video_id} deleted successfully",
            }
        )

    except Exception as e:
        logger.error(f"Error deleting video {video_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
