# Audio Module Service

The Audio Module service is a microservice that generates audio files for TOPIK-style questions using a TTS model. It processes questions stored in the shared database and generates audio clips for each question.

## Features

- Fetches questions and audio segments from the shared database using `video_id`.
- Generates audio files for each question using a Hugging Face TTS model.
- Stores the generated audio files in the shared `audio` directory.
- Updates the database with the paths to the generated audio files.
- Exposes Prometheus metrics for monitoring.
- Supports OpenTelemetry (OTEL) for distributed tracing.

## API Endpoints

### 1. Process Questions

**Endpoint:** `/api/process-questions/<video_id>`  
**Method:** `POST`

**Description:**
Generates audio files for all questions associated with the given `video_id`.

**Response:**

- Success:

  ```json
  {
    "success": true,
    "generated_audio": [
      {
        "question_id": 1,
        "audio_path": "shared/data/audio/example_video_id_1.wav"
      }
    ]
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
curl -X POST http://127.0.0.1:5002/api/process-questions/example_video_id
```

### 2. Retrieve Audio File

**Endpoint:** `/api/audio/<filename>`  
**Method:** `GET`

**Description:**
Fetches a specific audio file by its filename.

**Response:**

- Success: Returns the audio file as a `.wav` file.
- Error:

  ```json
  {
    "error": "Audio file not found"
  }
  ```

**Example Command:**

```bash
curl -X GET http://127.0.0.1:5002/api/audio/example_video_id_1.wav --output example_audio.wav
```

### 3. Health Check

**Endpoint:** `/health`  
**Method:** `GET`

**Response:**

```json
{
  "status": "ok"
}
```

**Example Command:**

```bash
curl -X GET http://127.0.0.1:5002/health
```

## Prometheus Metrics

Prometheus metrics are exposed at the `/metrics` endpoint. You can fetch them using:

```bash
curl -X GET http://127.0.0.1:5002/metrics
```

Example metrics:

```
# HELP audio_generated_total Total number of audio files generated
# TYPE audio_generated_total counter
audio_generated_total 3.0

# HELP tts_errors_total Total number of errors during TTS generation
# TYPE tts_errors_total counter
tts_errors_total 0.0
```

## OpenTelemetry (OTEL)

To test OpenTelemetry tracing:

1. Ensure the `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable is set to the OTEL collector endpoint.
2. Use a tool like Jaeger or Zipkin to view traces.

## Usage Examples

### Example 1: Process Questions

```bash
curl -X POST http://127.0.0.1:5002/api/process-questions/example_video_id
```

### Example 2: Fetch Prometheus Metrics

```bash
curl -X GET http://127.0.0.1:5002/metrics
```

### Example 3: Health Check

```bash
curl -X GET http://127.0.0.1:5002/health
```

### Example 4: Retrieve Audio File

```bash
curl -X GET http://127.0.0.1:5002/api/audio/example_video_id_1.wav --output example_audio.wav
```
