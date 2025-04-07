import os
from comps import (
    MegaService,
    MicroService,
    ServiceOrchestrator,
    ServiceGateway,
)
from comps.cores.mega.constants import ServiceType, ServiceRoleType
import logging
from services.question_module.app import QUESTIONS_GENERATED

logger = logging.getLogger(__name__)

# Define service host IPs and ports
TRANSCRIPT_SERVICE_HOST_IP = os.getenv(
    "TRANSCRIPT_SERVICE_HOST_IP", "transcript-processor"
)
TRANSCRIPT_SERVICE_PORT = int(os.getenv("TRANSCRIPT_SERVICE_PORT", 5000))
QUESTION_SERVICE_HOST_IP = os.getenv(
    "QUESTION_SERVICE_HOST_IP", "question-module"
)
QUESTION_SERVICE_PORT = int(os.getenv("QUESTION_SERVICE_PORT", 5001))
AUDIO_SERVICE_HOST_IP = os.getenv("AUDIO_SERVICE_HOST_IP", "audio-module")
AUDIO_SERVICE_PORT = int(os.getenv("AUDIO_SERVICE_PORT", 5002))
LLM_SERVICE_HOST_IP = os.getenv("OLLAMA_HOST", "ollama")
LLM_SERVICE_PORT = int(os.getenv("LLM_SERVICE_PORT", 11434))
MEGA_SERVICE_PORT = int(os.getenv("MEGA_SERVICE_PORT", 8000))


class KoreanListeningMegaService(MegaService):
    def __init__(self, host="0.0.0.0", port=MEGA_SERVICE_PORT):
        super().__init__()
        self.host = host
        self.port = port
        self.service_orchestrator = ServiceOrchestrator()

    def add_services(self):
        # YouTube transcript service
        self.transcript_service = MicroService(
            name="transcript_processor",
            host=TRANSCRIPT_SERVICE_HOST_IP,
            port=TRANSCRIPT_SERVICE_PORT,
            endpoint="/api/process",
            service_type=ServiceType.PROCESSOR,
            role_type=ServiceRoleType.EXTRACTOR,
        )

        # Question generation service
        self.question_service = MicroService(
            name="question_generator",
            host=QUESTION_SERVICE_HOST_IP,
            port=QUESTION_SERVICE_PORT,
            endpoint="/api/generate-questions",
            service_type=ServiceType.LLM,
            role_type=ServiceRoleType.GENERATOR,
        )

        # Audio generation service
        self.audio_service = MicroService(
            name="audio_generator",
            host=AUDIO_SERVICE_HOST_IP,
            port=AUDIO_SERVICE_PORT,
            endpoint="/api/tts",
            service_type=ServiceType.TTS,
            role_type=ServiceRoleType.GENERATOR,
        )

        # External LLM service
        self.llm_service = MicroService(
            name="llm",
            host=LLM_SERVICE_HOST_IP,
            port=LLM_SERVICE_PORT,
            endpoint="/api/generate",
            service_type=ServiceType.LLM,
            role_type=ServiceRoleType.GENERATOR,
        )

        # Register services
        self.service_orchestrator.add(self.transcript_service)
        self.service_orchestrator.add(self.question_service)
        self.service_orchestrator.add(self.audio_service)
        self.service_orchestrator.add(self.llm_service)

        # Create data flow between services
        self.service_orchestrator.flow_to(
            from_node=self.transcript_service.name,  # transcript_processor
            to_node=self.question_service.name,  # question_generator
            input_field="transcript",  # field to pass to question generator
            output_field="transcript",  # field from transcript processor output
        )

        self.service_orchestrator.flow_to(
            from_node=self.question_service.name,  # question_generator
            to_node=self.audio_service.name,  # audio_generator
            input_field="text",  # field for TTS input
            output_field="questions.question_text",  # field from question generator output
        )

    def create_gateway(self):
        self.gateway = ServiceGateway(
            megaservice=self.service_orchestrator,
            host=self.host,
            port=self.port,
        )

        # Register API endpoints
        @self.gateway.add_route("/health")
        async def health():
            return {"status": "ok"}

        @self.gateway.add_route("/api/process")
        async def process_full_request(request_data):
            return await self.process_request(request_data)

    async def process_request(self, request_data):
        try:
            video_url = request_data.get("video_url")
            num_questions = request_data.get(
                "num_questions", 3
            )  # Default to 3 questions

            # 1. Get transcript
            transcript_result = await self.service_orchestrator.schedule(
                service_name="transcript_processor",
                initial_inputs={"url": video_url},
            )

            # 2. Generate questions
            questions_result = await self.service_orchestrator.schedule(
                service_name="question_generator",
                initial_inputs={
                    "transcript": transcript_result,
                    "num_questions": num_questions,
                },
            )

            # 3. Generate audio for questions
            audio_results = []
            for question in questions_result.get("questions", []):
                audio_result = await self.service_orchestrator.schedule(
                    service_name="audio_generator",
                    initial_inputs={"text": question["question_text"]},
                )
                audio_results.append(audio_result)

            # Track metrics for question generation
            if questions_result and questions_result.get("questions"):
                for question in questions_result["questions"]:
                    QUESTIONS_GENERATED.labels(
                        difficulty_level=question["difficulty_level"],
                        content_type=question["content_type"],
                    ).inc()

            return {
                "success": True,
                "transcript": transcript_result,
                "questions": questions_result.get("questions", []),
                "audio_files": audio_results,
                "analytics": {
                    "video_duration": transcript_result["metadata"]["length"],
                    "question_count": len(
                        questions_result.get("questions", [])
                    ),
                    "difficulty_distribution": questions_result[
                        "metadata"
                    ].get("difficulty_distribution", {}),
                    "content_types": questions_result["metadata"].get(
                        "content_types", {}
                    ),
                },
            }
        except Exception as e:
            logger.error(f"Error in pipeline: {e}")
            raise

    def run(self):
        """Run the mega service"""
        self.add_services()
        self.create_gateway()
        print(
            f"Korean Listening Mega Service running on http://{self.host}:{self.port}"
        )
        self.gateway.run()  # Start the gateway service


if __name__ == "__main__":
    try:
        logger.info("Starting KoreanListeningMegaService...")
        mega_service = KoreanListeningMegaService()
        mega_service.run()
    except Exception as e:
        logger.error(f"Failed to start MegaService: {e}")
        raise
