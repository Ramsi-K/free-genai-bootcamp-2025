#!/usr/bin/env python
# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import os
import json
import re
import logging
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import requests
from datetime import datetime
from prometheus_client import Counter, generate_latest, REGISTRY, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Import from our local guardrails file
from guardrails import VideoGuardrails

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# --- Configuration ---
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/shared/data")
os.makedirs(OUTPUT_DIR, exist_ok=True)
DB_PATH = os.path.join(os.getcwd(), "..", "shared", "data", "app.db")
OTEL_EXPORTER_OTLP_ENDPOINT = os.environ.get(
    "OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317"
)  # Point to collector service name in docker-compose
SERVICE_NAME_OTEL = os.environ.get("SERVICE_NAME", "transcript-processor")
YOUTUBE_API_KEY = os.environ.get(
    "YOUTUBE_API_KEY"
)  # Get API key from environment

# Example: read blacklisted channels from environment variable
blacklisted_channels_str = os.getenv("BLACKLISTED_CHANNELS", "")
blacklisted_channels_list = [
    ch.strip() for ch in blacklisted_channels_str.split(",") if ch.strip()
]

guardrails = VideoGuardrails(
    blacklisted_channels=blacklisted_channels_list,
    min_duration=int(os.getenv("MIN_VIDEO_LENGTH", 60)),
    max_duration=int(os.getenv("MAX_VIDEO_LENGTH", 900)),
    min_transcript_length=int(os.getenv("MIN_TRANSCRIPT_LENGTH", 100)),
    max_transcript_length=int(os.getenv("MAX_TRANSCRIPT_LENGTH", 5000)),
    min_korean_ratio=float(os.getenv("MIN_KOREAN_RATIO", 0.7))
)

# --- Logging Setup ---
# Configure logging first so other modules can use it
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --- OTEL Setup ---
def init_telemetry():
    """Initialize OpenTelemetry tracing."""
    if not OTEL_EXPORTER_OTLP_ENDPOINT:
        logger.warning(
            "OTEL_EXPORTER_OTLP_ENDPOINT not set. Telemetry disabled."
        )
        return
    try:
        resource = Resource(attributes={SERVICE_NAME: SERVICE_NAME_OTEL})
        provider = TracerProvider(resource=resource)
        # Use insecure=True if collector endpoint is HTTP, False if HTTPS (and certs are set up)
        insecure_flag = OTEL_EXPORTER_OTLP_ENDPOINT.startswith("http://")
        otlp_exporter = OTLPSpanExporter(
            endpoint=OTEL_EXPORTER_OTLP_ENDPOINT, insecure=insecure_flag
        )
        span_processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(span_processor)
        trace.set_tracer_provider(provider)
        FlaskInstrumentor().instrument_app(app)
        logger.info(
            f"OpenTelemetry initialized for service: {SERVICE_NAME_OTEL}, exporting to {OTEL_EXPORTER_OTLP_ENDPOINT}"
        )
    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry: {e}")


# --- Prometheus Setup ---
# Initialize counters
TRANSCRIPTS_PROCESSED = Counter(
    "transcripts_processed_total",
    "Total number of transcripts successfully processed",
)
VIDEOS_PROCESSED = Counter(
    "videos_processed_total",
    "Total number of videos successfully processed (passed guardrails)",
)
PROCESSING_ERRORS = Counter(
    "processing_errors_total",
    "Total number of errors during video processing",
    [
        "error_type"
    ],  # e.g., 'metadata_fetch', 'transcript_fetch', 'guardrail', 'database'
)

# Add Prometheus metrics endpoint
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})


# --- Helper Functions (Preserved from original logic) ---
def extract_video_id(url):
    """Extract YouTube video ID from URL."""
    # Regex for standard, short, and embed URLs
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",  # Standard watch?v= or /v/
        r"(?:embed\/|v\/|youtu\.be\/)([0-9A-Za-z_-]{11})",  # Embed, v/, youtu.be
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            # Return the first captured group which should be the 11-char ID
            return match.group(1)
    logger.warning(f"Could not extract video ID from URL: {url}")
    return None


def get_video_metadata(video_id):
    """Get video metadata using YouTube Data API (or fallback)."""
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("get_video_metadata_internal") as span:
        span.set_attribute("video_id", video_id)
        try:
            if not YOUTUBE_API_KEY:
                logger.warning(
                    f"No YouTube API Key provided for video {video_id}. Using fallback metadata."
                )
                span.set_attribute("api_key_present", False)
                # Provide some default/fallback metadata
                return {
                    "title": f"Video {video_id} (No API Key)",
                    "author": "Unknown",
                    "description": "",
                    "length": 0,  # Indicate unknown length
                    "publish_date": None,
                    "views": 0,
                }
            span.set_attribute("api_key_present", True)
            url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={YOUTUBE_API_KEY}&part=snippet,contentDetails,statistics"
            response = requests.get(url, timeout=10)  # Add timeout
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            data = response.json()
            if not data.get("items"):
                logger.error(
                    f"Video not found or API error for {video_id}: {data}"
                )
                span.set_attribute("video_found", False)
                return None  # Indicate failure

            span.set_attribute("video_found", True)
            item = data["items"][0]
            snippet = item.get("snippet", {})
            content_details = item.get("contentDetails", {})
            statistics = item.get("statistics", {})

            duration_iso = content_details.get("duration")
            duration_seconds = (
                parse_duration(duration_iso) if duration_iso else 0
            )

            metadata = {
                "title": snippet.get("title", "Unknown Title"),
                "author": snippet.get("channelTitle", "Unknown Author"),
                "description": snippet.get("description", ""),
                "length": duration_seconds,
                "publish_date": snippet.get("publishedAt"),
                "views": int(statistics.get("viewCount", 0)),
            }
            logger.info(
                f"Successfully retrieved metadata for video {video_id}"
            )
            span.set_attributes(
                {  # Add multiple attributes
                    f"metadata.{k}": str(v)[
                        :200
                    ]  # Limit attribute value length
                    for k, v in metadata.items()
                    if v is not None
                }
            )
            return metadata

        except requests.exceptions.Timeout:
            logger.error(f"Timeout getting metadata for {video_id}")
            PROCESSING_ERRORS.labels(error_type="metadata_fetch_timeout").inc()
            span.record_exception(requests.exceptions.Timeout("API Timeout"))
            span.set_status(
                trace.Status(trace.StatusCode.ERROR, "Metadata fetch timeout")
            )
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP error getting metadata for {video_id}: {e}")
            PROCESSING_ERRORS.labels(error_type="metadata_fetch_http").inc()
            span.record_exception(e)
            span.set_status(
                trace.Status(
                    trace.StatusCode.ERROR, "Metadata fetch HTTP error"
                )
            )
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error getting metadata for {video_id}: {e}",
                exc_info=True,
            )
            PROCESSING_ERRORS.labels(error_type="metadata_fetch_other").inc()
            span.record_exception(e)
            span.set_status(
                trace.Status(
                    trace.StatusCode.ERROR, "Metadata fetch unexpected error"
                )
            )
            return None


def parse_duration(duration_iso):
    """Parse ISO 8601 duration format to seconds."""
    if not duration_iso or not isinstance(duration_iso, str):
        return 0
    try:
        # Regex supporting days, hours, minutes, seconds
        match = re.match(
            r"P(?:(?P<days>\d+)D)?T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>[\d.]+)S)?",
            duration_iso,
        )
        if not match:
            logger.warning(
                f"Could not parse ISO 8601 duration: {duration_iso}"
            )
            return 0

        parts = match.groupdict()
        time_in_seconds = 0
        time_in_seconds += int(parts.get("days", 0) or 0) * 86400
        time_in_seconds += int(parts.get("hours", 0) or 0) * 3600
        time_in_seconds += int(parts.get("minutes", 0) or 0) * 60
        time_in_seconds += float(
            parts.get("seconds", 0) or 0
        )  # Use float for seconds

        return int(time_in_seconds)  # Return integer seconds
    except Exception as e:
        logger.error(f"Error parsing duration '{duration_iso}': {e}")
        return 0  # Return 0 on error


def save_to_db(video_id, metadata, transcript_text, segments):
    """Save video metadata, transcript, and segments to SQLite database."""
    conn = None
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("save_to_database_internal") as span:
        span.set_attribute("video_id", video_id)
        span.set_attribute("segment_count", len(segments))
        try:
            # Use a context manager for the connection
            with sqlite3.connect(DB_PATH, timeout=10) as conn:  # Add timeout
                cursor = conn.cursor()
                # Use INSERT OR REPLACE to handle potential re-processing of the same video_id
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO videos (video_id, title, author, description, length, publish_date, views, transcript, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        video_id,
                        metadata.get("title", "Unknown Title"),
                        metadata.get("author", "Unknown Author"),
                        metadata.get("description", ""),
                        metadata.get("length", 0),
                        metadata.get("publish_date"),
                        metadata.get("views", 0),
                        transcript_text,
                        datetime.now().isoformat(),  # Explicitly set created_at on replace
                    ),
                )
                # Delete old segments for this video_id before inserting new ones
                cursor.execute(
                    "DELETE FROM segments WHERE video_id = ?", (video_id,)
                )
                # Save new segments if any exist
                segment_data = [
                    (
                        video_id,
                        seg["start"],
                        seg["end"],
                        seg["duration"],
                        seg["text"],
                    )
                    for seg in segments
                    if isinstance(seg, dict)  # Ensure segment is a dict
                ]
                if segment_data:
                    cursor.executemany(
                        """
                        INSERT INTO segments (video_id, start, end, duration, text)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        segment_data,
                    )
                # No explicit commit needed with 'with' statement, it commits on success, rolls back on error
            logger.info(
                f"Successfully saved data for video {video_id} to database."
            )
            span.set_attribute("db_save_successful", True)
            return True
        except sqlite3.Error as e:
            logger.error(
                f"Database error saving data for video {video_id}: {e}"
            )
            PROCESSING_ERRORS.labels(error_type="database_save").inc()
            span.record_exception(e)
            span.set_attribute("db_save_successful", False)
            span.set_status(
                trace.Status(trace.StatusCode.ERROR, "Database save error")
            )
            # Rollback is handled automatically by 'with' statement on exception
            return False
        except Exception as e:  # Catch other potential errors
            logger.error(
                f"Unexpected error saving data for video {video_id}: {e}",
                exc_info=True,
            )
            PROCESSING_ERRORS.labels(error_type="database_save_other").inc()
            span.record_exception(e)
            span.set_attribute("db_save_successful", False)
            span.set_status(
                trace.Status(
                    trace.StatusCode.ERROR, "Unexpected database save error"
                )
            )
            return False


def get_transcript(video_id):
    """Fetch Korean transcript for a YouTube video."""
    try:
        # Attempt to fetch the Korean transcript explicitly
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
        formatter = TextFormatter()
        transcript_text = formatter.format_transcript(transcript)
        segments = [
            {
                "start": entry["start"],
                "end": entry["start"] + entry["duration"],
                "duration": entry["duration"],
                "text": entry["text"],
            }
            for entry in transcript
        ]
        return transcript_text, segments
    except Exception as e:
        logger.error(f"Error fetching Korean transcript for video {video_id}: {e}")
        return None, []


# --- API Endpoints ---

@app.errorhandler(Exception)
def handle_exception(e):
    """Global error handler to log exceptions."""
    logger.error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500

@app.route("/")
def home():
    return "Welcome to the Transcript Processor API!", 200


@app.route("/api/process", methods=["POST"])
def process_video():
    """Process YouTube video: fetch metadata, transcript, validate, save."""
    video_url = request.json.get("url")
    if not video_url:
        return jsonify({"error": "URL is required"}), 400

    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        # Fetch metadata
        metadata = get_video_metadata(video_id)
        if not metadata:
            logger.error(f"Failed to fetch metadata for video ID: {video_id}")
            return jsonify({"error": "Failed to fetch video metadata"}), 500

        # Apply guardrails to metadata
        metadata_error = guardrails.validate_metadata(metadata)
        if metadata_error:
            logger.warning(f"Metadata validation failed: {metadata_error}")
            return jsonify({"error": metadata_error}), 400

        # Fetch transcript
        transcript_text, segments = get_transcript(video_id)
        if not transcript_text:
            logger.error(f"Failed to fetch transcript for video ID: {video_id}")
            return jsonify({"error": "Failed to fetch transcript"}), 500

        # Apply guardrails to transcript
        transcript_error = guardrails.validate_transcript(transcript_text)
        if transcript_error:
            logger.warning(f"Transcript validation failed: {transcript_error}")
            return jsonify({"error": transcript_error}), 400

        # Save to database
        save_to_db(video_id, metadata, transcript_text, segments)

        return jsonify({"success": True, "video_id": video_id})

    except Exception as e:
        logger.error(f"Error processing video: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/transcript/<video_id>", methods=["GET"])
def get_transcript_by_video_id(video_id):
    """Fetch transcript and metadata for a specific video ID."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Fetch video metadata
        cursor.execute("SELECT * FROM videos WHERE video_id = ?", (video_id,))
        video_row = cursor.fetchone()
        if not video_row:
            return jsonify({"error": "Video not found"}), 404

        # Map video metadata to a dictionary
        video_metadata = {
            "video_id": video_row[1],
            "title": video_row[2],
            "author": video_row[3],
            "description": video_row[4],
            "length": video_row[5],
            "publish_date": video_row[6],
            "views": video_row[7],
            "transcript": video_row[8],
        }

        # Fetch transcript segments
        cursor.execute("SELECT start, end, duration, text FROM segments WHERE video_id = ?", (video_id,))
        segments = [
            {"start": row[0], "end": row[1], "duration": row[2], "text": row[3]}
            for row in cursor.fetchall()
        ]

        conn.close()

        return jsonify({"video_id": video_id, "metadata": video_metadata, "segments": segments})

    except sqlite3.Error as e:
        logger.error(f"Database error while fetching transcript for video {video_id}: {e}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        logger.error(f"Unexpected error while fetching transcript for video {video_id}: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting the Flask app...")

    app.run(host="0.0.0.0", port=5000, debug=True)
