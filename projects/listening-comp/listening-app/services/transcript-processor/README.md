# Transcript Processor Service

The Transcript Processor service is a microservice that processes YouTube videos to extract metadata, transcripts, and segments. It validates the content using guardrails and stores the data in a shared SQLite database.

## Features

- Extracts metadata and transcripts from YouTube videos.
- Validates video and transcript content using guardrails.
- Stores metadata, transcripts, and segments in a shared SQLite database.
- Exposes Prometheus metrics for monitoring.
- Supports OpenTelemetry (OTEL) for distributed tracing.

## API Endpoints

### 1. Process a YouTube Video

**Endpoint:** `/api/process`  
**Method:** `POST`

**Request Body:**

```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response:**

- Success:

  ```json
  {
    "success": true,
    "video_id": "VIDEO_ID"
  }
  ```

- Error:

  ```json
  {
    "error": "Error message here"
  }
  ```

**Example Command:**

```bash
curl -X POST http://127.0.0.1:5000/api/process \
-H "Content-Type: application/json" \
-d '{"url": "https://www.youtube.com/watch?v=2J34NWxJZfo"}'
```

### 2. Fetch Transcript and Metadata

**Endpoint:** `/api/transcript/<video_id>`  
**Method:** `GET`

**Response:**

- Success:

  ```json
  {
    "video_id": "VIDEO_ID",
    "metadata": {
      "title": "Video Title",
      "author": "Channel Name",
      "description": "Video description",
      "length": 300,
      "publish_date": "2023-01-01T00:00:00Z",
      "views": 1000
    },
    "segments": [
      {
        "start": 0.0,
        "end": 10.0,
        "duration": 10.0,
        "text": "Segment text here"
      }
    ]
  }
  ```

- Error:

  ```json
  {
    "error": "Video not found"
  }
  ```

**Example Command:**

```bash
curl -X GET http://127.0.0.1:5000/api/transcript/2J34NWxJZfo
```

## Prometheus Metrics

Prometheus metrics are exposed at the `/metrics` endpoint. You can fetch them using:

```bash
curl -X GET http://127.0.0.1:5000/metrics
```

Example metrics:

```text
# HELP transcripts_processed_total Total number of transcripts successfully processed
# TYPE transcripts_processed_total counter
transcripts_processed_total 1.0
```

## OpenTelemetry (OTEL)

To test OpenTelemetry tracing:

1. Ensure the `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable is set to the OTEL collector endpoint.
2. Use a tool like Jaeger or Zipkin to view traces.

## Usage Examples

### Example 1: Process a Video

```bash
curl -X POST http://127.0.0.1:5000/api/process \
-H "Content-Type: application/json" \
-d '{"url": "https://www.youtube.com/watch?v=2J34NWxJZfo"}'
```

### Example 2: Fetch Transcript

```bash
curl -X GET http://127.0.0.1:5000/api/transcript/2J34NWxJZfo
```

### Example 3: Fetch Prometheus Metrics

```bash
curl -X GET http://127.0.0.1:5000/metrics
```
