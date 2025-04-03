import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import chromadb
from chromadb.utils import embedding_functions
from prometheus_client import Counter
from comps import MicroService, ServiceType, ServiceRoleType
from wrappers import ServiceWrapper, init_telemetry
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from docarray_shim import DocList  # Use compatibility wrapper for DocList

# Initialize OTEL
trace.set_tracer_provider(TracerProvider())
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
CORS(app)

# Initialize telemetry
init_telemetry(port=8001)  # Different port per service

# Create service wrapper
wrapper = ServiceWrapper("question_module")
# Configure logging
QUESTIONS_GENERATED = Counter(
    "questions_generated",
    "Number of questions generated",
    ["difficulty_level"],
)
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TopikQuestion:
    def __init__(self, question_text, choices, correct_answer, audio_segment):
        self.question_text = question_text  # The question text
        self.choices = choices  # List of 4 possible answers
        self.correct_answer = correct_answer  # Index of correct answer
        self.audio_segment = audio_segment  # Timestamp info for audio
        self.audio_url = None  # Will be filled by TTS service
        self.explanation = None  # Explanation for the answer


class QuestionGenerator:
    def __init__(self):
        self.collection = self._setup_chroma()
        self.llm_service = MicroService(
            name="llm",
            host=os.getenv("OLLAMA_HOST", "ollama"),
            port=11434,
            endpoint="/api/generate",
            service_type=ServiceType.LLM,
            role_type=ServiceRoleType.GENERATOR,
        )
        self.min_segment_duration = 20
        self.max_questions_per_minute = 2

    def _setup_chroma(self):
        try:
            embedding_function = (
                embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=os.getenv(
                        "EMBEDDING_MODEL", "jhgan/ko-sroberta-multitask"
                    )
                )
            )
        except Exception:
            logger.error(
                f"Failed to load specified embedding model, falling back to default"
            )
            embedding_function = (
                embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
            )

        try:
            client = chromadb.PersistentClient(
                path=os.getenv("CHROMA_DIR", "/shared/data/chroma")
            )
            collection = client.get_or_create_collection(
                name="korean_transcripts",
                embedding_function=embedding_function,
                metadata={"hnsw:space": "cosine"},
            )
            return collection
        except Exception as e:
            logger.error(f"Error setting up ChromaDB: {e}")
            raise

    async def store_vectors(self, embeddings, text):
        try:
            self.collection.add(
                embeddings=embeddings,
                documents=[text],
                ids=[f"doc_{len(self.collection.get()['ids'])}"],
            )
            return {"success": True}
        except Exception as e:
            logging.error(f"Error storing vectors: {e}")
            raise

    async def generate_topik_questions(self, transcript_data):
        """Generate TOPIK-style listening comprehension questions"""
        try:
            segments = transcript_data.get("segments", [])
            total_duration = sum(seg["duration"] for seg in segments)
            max_questions_by_duration = int(
                (total_duration / 60) * self.max_questions_per_minute
            )
            num_questions = transcript_data.get(
                "num_questions", 3
            )  # Get desired number of questions
            max_questions = min(
                num_questions, max_questions_by_duration
            )  # Use the smaller value

            # Filter segments that are too short
            valid_segments = [
                s
                for s in segments
                if s["duration"] >= self.min_segment_duration
            ]

            # Group segments by topic/context using embeddings
            grouped_segments = self._group_segments_by_topic(valid_segments)

            questions = []
            for group in grouped_segments:
                # Generate questions based on content type and difficulty
                segment_type = self._detect_content_type(
                    group["text"]
                )  # news, conversation, etc.
                difficulty = self._assess_difficulty(
                    group["text"]
                )  # TOPIK 1-6 levels

                prompt = self._create_topik_prompt(
                    text=group["text"],
                    content_type=segment_type,
                    difficulty=difficulty,
                )

                response = await self.llm_service.generate(prompt)

                question = TopikQuestion(
                    question_text=response["question"],
                    choices=response["choices"],
                    correct_answer=response["correct_index"],
                    audio_segment=group["timestamp"],
                    difficulty_level=difficulty,
                    content_type=segment_type,
                )
                questions.append(question)

                # Don't exceed max questions
                if len(questions) >= max_questions:
                    break

            return {
                "success": True,
                "questions": [q.__dict__ for q in questions],
                "metadata": {
                    "total_duration": total_duration,
                    "difficulty_distribution": self._get_difficulty_distribution(
                        questions
                    ),
                    "content_types": self._get_content_types(questions),
                },
            }
        except Exception as e:
            logging.error(f"Error generating TOPIK questions: {e}")
            raise

    def _create_topik_prompt(self, text, content_type, difficulty):
        """Create appropriate prompt based on content type and difficulty"""
        prompts = {
            "news": """다음 뉴스 내용을 듣고 TOPIK {difficulty}급 수준의 청취 문제를 만드세요:
                    {text}
                    
                    문제 형식:
                    - 뉴스의 주요 내용을 파악하는 질문
                    - 4개의 선택지 (가,나,다,라)
                    - 정답 표시""",
            "conversation": """다음 대화를 듣고 TOPIK {difficulty}급 수준의 청취 문제를 만드세요:
                    {text}
                    
                    문제 형식:
                    - 대화의 상황이나 목적을 파악하는 질문
                    - 4개의 선택지 (가,나,다,라)
                    - 정답 표시""",
        }
        return prompts.get(content_type, "").format(
            text=text, difficulty=difficulty
        )


generator = QuestionGenerator()


@app.route("/api/store-vectors", methods=["POST"])
@wrapper.endpoint_handler("store_vectors")
async def store_vectors():
    data = request.json
    return await generator.store_vectors(data["embeddings"], data["text"])


@app.route("/api/generate-questions", methods=["POST"])
@wrapper.endpoint_handler("generate_questions")
async def generate_questions():
    try:
        data = request.json
        transcript = data["transcript"]
        num_questions = data.get(
            "num_questions", 3
        )  # Get num_questions, default to 3
        result = await generator.generate_topik_questions(
            {"transcript": transcript, "num_questions": num_questions}
        )
        QUESTIONS_GENERATED.labels(difficulty_level="topik").inc()

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
@wrapper.endpoint_handler("health_check")
async def health_check():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
