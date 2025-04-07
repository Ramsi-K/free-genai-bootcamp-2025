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
from prometheus_client import Counter, generate_latest, REGISTRY
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Import from our local guardrails file
from guardrails import VideoGuardrails, is_korean_content

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# --- Configuration ---
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/shared/data")
os.makedirs(OUTPUT_DIR, exist_ok=True)
DB_PATH = os.path.join(OUTPUT_DIR, "transcripts.db")
OTEL_EXPORTER_OTLP_ENDPOINT = os.environ.get(
    "OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317"
)  # Point to collector service name in docker-compose
SERVICE_NAME_OTEL = os.environ.get("SERVICE_NAME", "transcript-processor")
YOUTUBE_API_KEY = os.environ.get(
    "YOUTUBE_API_KEY"
)  # Get API key from environment

# --- Logging Setup ---
# Configure logging first so other modules can use it
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# --- Database Setup ---
def init_db():
    """Initialize the SQLite database and tables."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Videos table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE NOT NULL,
                title TEXT,
                author TEXT,
                description TEXT,
                length INTEGER,
                publish_date TEXT,
                views INTEGER,
                transcript TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        # Segments table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS segments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                start REAL,
                end REAL,
                duration REAL,
                text TEXT,
                FOREIGN KEY(video_id) REFERENCES videos(video_id) ON DELETE CASCADE
            )
        """
        )  # Added ON DELETE CASCADE
        conn.commit()
        logger.info(f"Database initialized successfully at {DB_PATH}")
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}")
        # Consider how critical DB is. If essential, maybe raise exception?
    finally:
        if conn:
            conn.close()


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

# --- Guardrails Setup ---
# Example: read blacklisted channels from environment variable
blacklisted_channels_str = os.getenv("BLACKLISTED_CHANNELS", "")
blacklisted_channels_list = [
    ch.strip() for ch in blacklisted_channels_str.split(",") if ch.strip()
]

guardrails = VideoGuardrails(
    blacklisted_channels=blacklisted_channels_list,
    min_video_length=int(os.getenv("MIN_VIDEO_LENGTH", 60)),
    min_transcript_length=int(os.getenv("MIN_TRANSCRIPT_LENGTH", 50)),
)


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


# --- API Endpoints (No OPEA wrappers) ---


@app.route("/api/process", methods=["POST"])
def process_video():
    """Process YouTube video: fetch metadata, transcript, validate, save."""
    # Note: OTEL FlaskInstrumentor automatically creates a span for the request
    tracer = trace.get_tracer(__name__)
    current_span = (
        trace.get_current_span()
    )  # Get the span created by FlaskInstrumentor

    video_url = None  # Initialize for error logging
    video_id = None
    try:
        data = request.json
        if not data or "url" not in data:
            logger.warning("Process request failed: URL missing.")
            PROCESSING_ERRORS.labels(error_type="bad_request").inc()
            current_span.set_attribute("error", "URL missing")
            current_span.set_status(
                trace.Status(
                    trace.StatusCode.ERROR, "Bad Request: URL missing"
                )
            )
            return jsonify({"error": "URL is required"}), 400

        video_url = data["url"]  # Assign here for logging
        current_span.set_attribute("video_url", video_url)
        logger.info(f"Processing request for URL: {video_url}")

        video_id = extract_video_id(video_url)
        if not video_id:
            logger.warning(f"Invalid YouTube URL format: {video_url}")
            PROCESSING_ERRORS.labels(error_type="invalid_url").inc()
            current_span.set_attribute("error", "Invalid URL")
            current_span.set_status(
                trace.Status(
                    trace.StatusCode.ERROR, "Bad Request: Invalid URL"
                )
            )
            return jsonify({"error": "Invalid YouTube URL"}), 400
        current_span.set_attribute("video_id", video_id)

        # --- Check if already processed --- #
        # Use context manager for DB connection
        try:
            with sqlite3.connect(DB_PATH, timeout=5) as conn_check:
                cursor_check = conn_check.cursor()
                # Check if video exists
                cursor_check.execute(
                    "SELECT id, created_at FROM videos WHERE video_id = ?",
                    (video_id,),
                )
                exists = cursor_check.fetchone()
                if exists:
                    logger.info(
                        f"Video {video_id} already processed on {exists[1]}. Skipping."
                    )
                    current_span.set_attribute(
                        "processing_skipped", "already_exists"
                    )
                    # Return success, indicating it's already done
                    return (
                        jsonify(
                            {
                                "success": True,
                                "message": "Video already processed",
                                "video_id": video_id,
                            }
                        ),
                        200,
                    )  # 200 OK is fine here
        except sqlite3.Error as e:
            logger.error(
                f"Database error checking for existing video {video_id}: {e}"
            )
            # Continue processing, but log the error and mark span
            PROCESSING_ERRORS.labels(error_type="database_check").inc()
            current_span.set_attribute("db_check_error", str(e))
            # Do not fail the request here, attempt processing anyway

        # --- Metadata --- #
        metadata = get_video_metadata(
            video_id
        )  # This function now includes its own span
        if not metadata:
            logger.error(f"Failed to retrieve metadata for video {video_id}.")
            # Error already counted & logged in get_video_metadata
            current_span.set_attribute("error", "Metadata fetch failed")
            current_span.set_status(
                trace.Status(trace.StatusCode.ERROR, "Metadata fetch failed")
            )
            # Use 502 Bad Gateway if upstream API failed, 500 otherwise
            return (
                jsonify({"error": "Failed to retrieve video metadata."}),
                502,
            )

        # --- Metadata Guardrails --- #
        with tracer.start_as_current_span(
            "validate_metadata"
        ) as meta_guard_span:
            meta_guard_span.set_attribute("video_id", video_id)
            metadata_error = guardrails.validate_video_metadata(metadata)
            if metadata_error:
                logger.warning(
                    f"Metadata validation failed for {video_id}: {metadata_error}"
                )
                PROCESSING_ERRORS.labels(error_type="guardrail_metadata").inc()
                meta_guard_span.set_attribute("validation_failed", True)
                meta_guard_span.set_attribute("failure_reason", metadata_error)
                meta_guard_span.set_status(
                    trace.Status(
                        trace.StatusCode.ERROR,
                        f"Guardrail failed: {metadata_error}",
                    )
                )
                current_span.set_attribute(
                    "error", f"Guardrail failed: {metadata_error}"
                )
                return (
                    jsonify({"error": metadata_error}),
                    400,
                )  # Bad request due to invalid content
            meta_guard_span.set_attribute("validation_passed", True)

        # --- Transcript --- #
        transcript_text = None
        segments = []
        with tracer.start_as_current_span("get_transcript") as trans_span:
            trans_span.set_attribute("video_id", video_id)
            transcript_language = "unknown"  # Default
            try:
                # Find available transcripts
                transcript_list = YouTubeTranscriptApi.list_transcripts(
                    video_id
                )
                # Try to fetch Korean first, fallback to generated Korean or English
                transcript = None
                try:
                    transcript = transcript_list.find_transcript(["ko"])
                    logger.info(
                        f"Found manually created Korean transcript for {video_id}."
                    )
                    transcript_language = "ko_manual"
                except YouTubeTranscriptApi.NoTranscriptFound:
                    logger.info(
                        f"Manual Korean transcript not found for {video_id}, trying generated."
                    )
                    try:
                        # If manual Korean not found, try generated Korean or English
                        transcript = transcript_list.find_generated_transcript(
                            ["ko", "en"]
                        )
                        logger.info(
                            f"Found generated {transcript.language} transcript for {video_id}."
                        )
                        transcript_language = (
                            f"generated_{transcript.language}"
                        )
                    except YouTubeTranscriptApi.NoTranscriptFound as e_gen:
                        logger.error(
                            f"Could not find suitable transcript (Korean or English) for {video_id}: {e_gen}",
                            exc_info=False,
                        )  # Less verbose log
                        PROCESSING_ERRORS.labels(
                            error_type="transcript_fetch_unavailable"
                        ).inc()
                        trans_span.record_exception(e_gen)
                        trans_span.set_status(
                            trace.Status(
                                trace.StatusCode.ERROR,
                                "Transcript unavailable",
                            )
                        )
                        current_span.set_attribute(
                            "error", "Transcript unavailable"
                        )
                        return (
                            jsonify(
                                {
                                    "error": "Could not find a suitable Korean or English transcript."
                                }
                            ),
                            404,
                        )  # Not Found

                trans_span.set_attribute(
                    "transcript_type", transcript_language
                )

                # Fetch the actual transcript data
                transcript_data = transcript.fetch()
                formatter = TextFormatter()
                transcript_text = formatter.format_transcript(transcript_data)

                # Segment transcript
                for entry in transcript_data:
                    segments.append(
                        {
                            "start": entry.get("start"),
                            "end": entry.get("start", 0)
                            + entry.get("duration", 0),
                            "duration": entry.get("duration"),
                            "text": entry.get("text", "").strip(),
                        }
                    )
                logger.info(
                    f"Successfully fetched and segmented transcript ({transcript.language}) for {video_id}"
                )
                trans_span.set_attribute(
                    "transcript_language", transcript.language
                )
                trans_span.set_attribute("segment_count", len(segments))

            except YouTubeTranscriptApi.CouldNotRetrieveTranscript as e_fetch:
                logger.error(
                    f"Could not retrieve transcript for {video_id}: {e_fetch}",
                    exc_info=False,
                )
                PROCESSING_ERRORS.labels(
                    error_type="transcript_fetch_error"
                ).inc()
                trans_span.record_exception(e_fetch)
                trans_span.set_status(
                    trace.Status(
                        trace.StatusCode.ERROR, "Transcript retrieval failed"
                    )
                )
                current_span.set_attribute(
                    "error", "Transcript retrieval failed"
                )
                # Return 404 if transcript specifically not found for this video
                return (
                    jsonify(
                        {
                            "error": f"Transcript not available for video {video_id}: {e_fetch}"
                        }
                    ),
                    404,
                )
            except Exception as e_fetch:
                logger.error(
                    f"Failed to fetch or format transcript for {video_id}: {e_fetch}",
                    exc_info=True,
                )
                PROCESSING_ERRORS.labels(
                    error_type="transcript_fetch_error"
                ).inc()
                trans_span.record_exception(e_fetch)
                trans_span.set_status(
                    trace.Status(
                        trace.StatusCode.ERROR, "Transcript fetch/format error"
                    )
                )
                current_span.set_attribute(
                    "error", "Transcript fetch/format error"
                )
                return (
                    jsonify(
                        {"error": "Failed to retrieve or format transcript."}
                    ),
                    500,
                )

        # --- Transcript Guardrails --- #
        with tracer.start_as_current_span(
            "validate_transcript"
        ) as trans_guard_span:
            trans_guard_span.set_attribute("video_id", video_id)
            # 1. Check language
            if not is_korean_content(transcript_text):
                logger.warning(
                    f"Transcript validation failed for {video_id}: Not Korean content."
                )
                PROCESSING_ERRORS.labels(error_type="guardrail_language").inc()
                trans_guard_span.set_attribute("validation_failed", True)
                trans_guard_span.set_attribute("failure_reason", "Not Korean")
                trans_guard_span.set_status(
                    trace.Status(
                        trace.StatusCode.ERROR, "Guardrail failed: Not Korean"
                    )
                )
                current_span.set_attribute(
                    "error", "Guardrail failed: Not Korean"
                )
                return (
                    jsonify(
                        {"error": "Transcript is not primarily in Korean."}
                    ),
                    400,
                )  # Bad request
            trans_guard_span.set_attribute("language_check_passed", True)

            # 2. Check content length/other rules
            transcript_error = guardrails.validate_transcript(transcript_text)
            if transcript_error:
                logger.warning(
                    f"Transcript validation failed for {video_id}: {transcript_error}"
                )
                PROCESSING_ERRORS.labels(error_type="guardrail_content").inc()
                trans_guard_span.set_attribute("validation_failed", True)
                trans_guard_span.set_attribute(
                    "failure_reason", transcript_error
                )
                trans_guard_span.set_status(
                    trace.Status(
                        trace.StatusCode.ERROR,
                        f"Guardrail failed: {transcript_error}",
                    )
                )
                current_span.set_attribute(
                    "error", f"Guardrail failed: {transcript_error}"
                )
                return jsonify({"error": transcript_error}), 400  # Bad request
            trans_guard_span.set_attribute("content_check_passed", True)
            trans_guard_span.set_attribute(
                "validation_passed", True
            )  # Overall transcript validation

        # --- Save to DB --- #
        if not save_to_db(video_id, metadata, transcript_text, segments):
            # Error already logged and counted in save_to_db
            current_span.set_attribute("error", "Database save failed")
            current_span.set_status(
                trace.Status(trace.StatusCode.ERROR, "Database save failed")
            )
            # Return 500 Internal Server Error if DB save fails
            return jsonify({"error": "Failed to save data to database."}), 500

        # --- Success --- #
        TRANSCRIPTS_PROCESSED.inc()
        VIDEOS_PROCESSED.inc()
        logger.info(f"Successfully processed video {video_id}")
        current_span.set_attribute("processing_successful", True)
        current_span.set_status(trace.Status(trace.StatusCode.OK))
        return jsonify(
            {
                "success": True,
                "video_id": video_id,
                "message": "Video processed successfully.",
                # Return metadata/segments only if needed by the immediate caller
                # "metadata": metadata,
                # "segments": segments
            }
        )

    except Exception as e:
        # Catch-all for unexpected errors in the main processing flow
        video_id_str = video_id if video_id else "N/A"
        url_str = video_url if video_url else "N/A"
        logger.error(
            f"Unhandled error during video processing for URL {url_str} (ID: {video_id_str}): {e}",
            exc_info=True,
        )
        PROCESSING_ERRORS.labels(error_type="unknown").inc()
        # Record exception in the main request span if possible
        if current_span:
            current_span.record_exception(e)
            current_span.set_attribute("error", "Unhandled exception")
            current_span.set_status(
                trace.Status(trace.StatusCode.ERROR, "Unhandled exception")
            )
            current_span.set_attribute(
                "processing_failed", True
            )  # Mark as failed
        return (
            jsonify(
                {"error": "An unexpected error occurred during processing."}
            ),
            500,
        )


@app.route("/api/videos", methods=["GET"])
def list_videos():
    """List all processed videos from the database."""
    conn = None
    try:
        # Use context manager for DB connection
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
            cursor = conn.cursor()
            # Select columns needed for the list view
            cursor.execute(
                """
                SELECT video_id, title, author, length, publish_date, views, created_at
                FROM videos
                ORDER BY created_at DESC
            """
            )
            videos = [dict(row) for row in cursor.fetchall()]
        return jsonify({"success": True, "videos": videos})
    except sqlite3.Error as e:
        logger.error(f"Database error listing videos: {e}")
        PROCESSING_ERRORS.labels(error_type="database_list_videos").inc()
        return jsonify({"error": "Failed to retrieve video list."}), 500
    except Exception as e:
        logger.error(f"Unexpected error listing videos: {e}", exc_info=True)
        PROCESSING_ERRORS.labels(error_type="list_videos_unknown").inc()
        return (
            jsonify(
                {"error": "An unexpected error occurred while listing videos."}
            ),
            500,
        )


@app.route("/api/transcript/<video_id>", methods=["GET"])
def get_transcript(video_id):
    """Get transcript and segments for a specific video_id."""
    conn = None
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("get_transcript_request") as span:
        span.set_attribute("video_id", video_id)
        try:
            # Use context manager for DB connection
            with sqlite3.connect(DB_PATH, timeout=10) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                # Get transcript text
                cursor.execute(
                    "SELECT transcript FROM videos WHERE video_id = ?",
                    (video_id,),
                )
                video_row = cursor.fetchone()
                if not video_row:
                    logger.warning(
                        f"Transcript requested for non-existent video_id: {video_id}"
                    )
                    span.set_attribute("video_found", False)
                    span.set_status(
                        trace.Status(trace.StatusCode.ERROR, "Video not found")
                    )
                    return jsonify({"error": "Video not found"}), 404
                transcript_text = video_row["transcript"]
                span.set_attribute("video_found", True)

                # Get segments
                cursor.execute(
                    "SELECT start, end, duration, text FROM segments WHERE video_id = ? ORDER BY start ASC",
                    (video_id,),
                )
                segments = [dict(row) for row in cursor.fetchall()]
                span.set_attribute("segment_count", len(segments))

            span.set_status(trace.Status(trace.StatusCode.OK))
            return jsonify(
                {
                    "success": True,
                    "video_id": video_id,
                    "transcript": transcript_text,
                    "segments": segments,
                }
            )
        except sqlite3.Error as e:
            logger.error(
                f"Database error getting transcript for {video_id}: {e}"
            )
            PROCESSING_ERRORS.labels(
                error_type="database_get_transcript"
            ).inc()
            span.record_exception(e)
            span.set_status(
                trace.Status(trace.StatusCode.ERROR, "Database error")
            )
            return (
                jsonify({"error": "Failed to retrieve transcript data."}),
                500,
            )
        except Exception as e:
            logger.error(
                f"Unexpected error getting transcript for {video_id}: {e}",
                exc_info=True,
            )
            PROCESSING_ERRORS.labels(error_type="get_transcript_unknown").inc()
            span.record_exception(e)
            span.set_status(
                trace.Status(trace.StatusCode.ERROR, "Unexpected error")
            )
            return jsonify({"error": "An unexpected error occurred."}), 500


@app.route("/metrics")
def metrics():
    """Expose Prometheus metrics."""
    # Use generate_latest from prometheus_client
    return (
        generate_latest(REGISTRY),
        200,
        {"Content-Type": "text/plain; version=0.0.4"},
    )


@app.route("/health")
def health_check():
    """Health check endpoint."""
    # Basic check: Can we connect to the DB?
    conn = None
    db_status = "unhealthy"  # Default to unhealthy
    try:
        # Use a short timeout for health check connection
        with sqlite3.connect(DB_PATH, timeout=2) as conn:
            # Check if the videos table exists as a basic schema check
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='videos';"
            )
            if cursor.fetchone():
                db_status = "healthy"
            else:
                logger.warning(
                    "Health check: 'videos' table not found in database."
                )
                db_status = "unhealthy (schema missing)"
    except sqlite3.Error as e:
        logger.error(f"Health check failed: DB connection/query error: {e}")
        # db_status remains 'unhealthy'
    except Exception as e:
        logger.error(f"Health check failed: Unexpected error: {e}")
        # db_status remains 'unhealthy'

    if db_status == "healthy":
        return jsonify({"status": "healthy", "database": db_status})
    else:
        # Return 503 Service Unavailable if DB is unhealthy
        return jsonify({"status": "unhealthy", "database": db_status}), 503


# --- Main Execution ---
if __name__ == "__main__":
    logger.info("Starting Transcript Processor Service in development mode...")
    init_db()  # Initialize DB on startup
    init_telemetry()  # Initialize OTEL
    # Use Flask's development server for local testing (Gunicorn is used in Dockerfile)
    # Enable debug mode for easier local development and auto-reloading
    app.run(host="0.0.0.0", port=5000, debug=True)
else:
    # If run with Gunicorn (like in the Dockerfile CMD), initialize here
    # Gunicorn pre-fork model might require careful handling of shared resources
    # if using multiple workers, but for DB connection pooling and OTEL,
    # initializing in the master process before forking is generally okay.
    init_db()
    init_telemetry()
    logger.info("Transcript Processor Service initialized for Gunicorn.")
    # Gunicorn will find the 'app' object automatically
