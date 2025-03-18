from functools import wraps
import time
import logging
from prometheus_client import Counter, Histogram, start_http_server
import os
from services.metrics.persistence import MetricsPersistence

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "request_total", "Total request count", ["service", "endpoint"]
)
REQUEST_LATENCY = Histogram(
    "request_latency_seconds", "Request latency", ["service", "endpoint"]
)
ERROR_COUNT = Counter(
    "error_total", "Total error count", ["service", "endpoint", "error_type"]
)

# Korean Learning Specific Metrics
QUESTIONS_GENERATED = Counter(
    "korean_questions_total", "Total questions generated", ["difficulty_level"]
)
AUDIO_GENERATED = Counter("korean_audio_total", "Total audio files generated")
TRANSCRIPT_LENGTH = Histogram(
    "korean_transcript_length_seconds", "Length of processed transcripts"
)
COMPREHENSION_SCORE = Histogram(
    "korean_comprehension_score",
    "User comprehension scores",
    ["difficulty_level"],
)


class ServiceWrapper:
    def __init__(self, service_name):
        self.service_name = service_name
        self.metrics_persistence = MetricsPersistence()

    def endpoint_handler(self, endpoint_name):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    # Track request
                    REQUEST_COUNT.labels(
                        self.service_name, endpoint_name
                    ).inc()

                    # Execute handler
                    result = await func(*args, **kwargs)

                    # Track latency
                    REQUEST_LATENCY.labels(
                        self.service_name, endpoint_name
                    ).observe(time.time() - start_time)

                    # Store metrics persistently
                    self.metrics_persistence.store_metric(
                        f"{self.service_name}_{endpoint_name}_latency",
                        time.time() - start_time,
                    )

                    return result
                except Exception as e:
                    # Track errors
                    ERROR_COUNT.labels(
                        self.service_name, endpoint_name, type(e).__name__
                    ).inc()
                    logger.error(f"Error in {endpoint_name}: {str(e)}")
                    raise

            return wrapper

        return decorator


def init_telemetry(port=8000):
    """Initialize Prometheus metrics server"""
    try:
        start_http_server(port)
        logger.info(f"Telemetry server started on port {port}")
    except Exception as e:
        logger.error(f"Failed to start telemetry server: {e}")
