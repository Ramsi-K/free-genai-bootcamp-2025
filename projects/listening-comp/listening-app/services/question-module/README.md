# Question Module Service

The Question Module service is a microservice that generates TOPIK-style Korean language listening comprehension questions from a transcript. It uses a local LLM (Ollama) to generate multiple-choice questions and stores the results in a shared SQLite database.

## Features

- Accepts a Korean transcript and generates 1–5 multiple-choice questions.
- Each question includes 4 answer choices, the correct answer, and the relevant transcript section.
- Stores the generated questions, choices, correct answers, and audio segments in a SQLite database.
- Exposes Prometheus metrics for monitoring.
- Supports OpenTelemetry (OTEL) for distributed tracing.

## API Endpoints

### 1. Generate Questions

**Endpoint:** `/api/generate-questions`  
**Method:** `POST`

**Request Body:**

```json
{
  "transcript": "여기 한국어 대본이 있습니다. 이 대본을 기반으로 질문을 생성하세요.",
  "video_id": "example_video_id",
  "num_questions": 3
}
```

**Response:**

- Success:

  ```json
  {
    "success": true,
    "questions": [
      {
        "question_text": "<question text in Korean>",
        "choices": [
          "<choice1 in Korean>",
          "<choice2 in Korean>",
          "<choice3 in Korean>",
          "<choice4 in Korean>"
        ],
        "correct_answer": 0,
        "audio_segment": "<relevant transcript section>"
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
curl -X POST http://127.0.0.1:5001/api/generate-questions \
-H "Content-Type: application/json" \
-d '{
  "transcript": "여기 한국어 대본이 있습니다. 이 대본을 기반으로 질문을 생성하세요.",
  "video_id": "example_video_id",
  "num_questions": 3
}'
```

### 2. Health Check

**Endpoint:** `/health`  
**Method:** `GET`

**Response:**

```json
{
  "status": "healthy"
}
```

**Example Command:**

```bash
curl -X GET http://127.0.0.1:5001/health
```

## Prometheus Metrics

Prometheus metrics are exposed at the `/metrics` endpoint. You can fetch them using:

```bash
curl -X GET http://127.0.0.1:5001/metrics
```

Example metrics:

```
# HELP questions_generated_total Total number of questions generated
# TYPE questions_generated_total counter
questions_generated_total 3.0

# HELP llm_errors_total Total number of errors during LLM calls
# TYPE llm_errors_total counter
llm_errors_total 0.0
```

## OpenTelemetry (OTEL)

To test OpenTelemetry tracing:

1. Ensure the `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable is set to the OTEL collector endpoint.
2. Use a tool like Jaeger or Zipkin to view traces.

## Usage Examples

### Example 1: Generate Questions

```bash
curl -X POST http://127.0.0.1:5001/api/generate-questions \
-H "Content-Type: application/json" \
-d '{
  "transcript": "여기 한국어 대본이 있습니다. 이 대본을 기반으로 질문을 생성하세요.",
  "video_id": "example_video_id",
  "num_questions": 3
}'
```

### Example 2: Fetch Prometheus Metrics

```bash
curl -X GET http://127.0.0.1:5001/metrics
```

### Example 3: Health Check

```bash
curl -X GET http://127.0.0.1:5001/health
```
