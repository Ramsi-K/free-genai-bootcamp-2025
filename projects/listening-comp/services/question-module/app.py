import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import chromadb
from chromadb.utils import embedding_functions
import asyncio
from functools import wraps
from comps import MicroService, ServiceType, ServiceRoleType
from wrappers import ServiceWrapper, init_telemetry
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    def _setup_chroma(self):
        try:
            embedding_function = (
                embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="jhgan/ko-sroberta-multitask"
                )
            )
        except:
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

    async def generate_questions(self, text):
        try:
            # Generate questions using LLM
            # ... existing question generation code ...
            return {"success": True, "questions": questions}
        except Exception as e:
            logging.error(f"Error generating questions: {e}")
            raise


generator = QuestionGenerator()


@app.route("/api/store-vectors", methods=["POST"])
@wrapper.endpoint_handler("store_vectors")
async def store_vectors():
    data = request.json
    return await generator.store_vectors(data["embeddings"], data["text"])


@app.route("/api/generate-questions", methods=["POST"])
@wrapper.endpoint_handler("generate_questions")
async def generate_questions():
    data = request.json
    result = await generator.generate_questions(data["text"])
    # Add Korean metrics
    QUESTIONS_GENERATED.labels(difficulty_level="intermediate").inc()
    return result


# Add health check endpoint
@app.route("/health", methods=["GET"])
@wrapper.endpoint_handler("health_check")
async def health_check():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
