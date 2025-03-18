from comps import MegaService, MicroService, ServiceOrchestrator
from comps.cores.mega.constants import ServiceType, ServiceRoleType
import os
import asyncio
import logging

logger = logging.getLogger(__name__)


class KoreanListeningMegaService(MegaService):
    def __init__(self):
        super().__init__()
        self.service_orchestrator = ServiceOrchestrator()

        # YouTube transcript service
        self.transcript_service = MicroService(
            name="transcript_processor",
            host="transcript-processor",
            port=5000,
            endpoint="/api/process",
            service_type=ServiceType.PROCESSOR,
            role_type=ServiceRoleType.EXTRACTOR,
        )

        # Question generation service (includes embedding and vector storage)
        self.question_service = MicroService(
            name="question_generator",
            host="question-module",
            port=5001,
            endpoint="/api/generate-questions",
            service_type=ServiceType.LLM,
            role_type=ServiceRoleType.GENERATOR,
        )

        # Audio generation service
        self.audio_service = MicroService(
            name="audio_generator",
            host="audio-module",
            port=5002,
            endpoint="/api/tts",
            service_type=ServiceType.TTS,
            role_type=ServiceRoleType.GENERATOR,
        )

        # External LLM service
        self.llm_service = MicroService(
            name="llm",
            host=os.getenv("OLLAMA_HOST", "ollama"),
            port=11434,
            endpoint="/api/generate",
            service_type=ServiceType.LLM,
            role_type=ServiceRoleType.GENERATOR,
        )

        # Register services
        for service in [
            self.transcript_service,
            self.question_service,
            self.audio_service,
            self.llm_service,
        ]:
            self.service_orchestrator.add(service)

    async def process_request(self, request_data):
        try:
            video_id = request_data.get("video_id")

            # 1. Get transcript
            transcript_result = await self.service_orchestrator.schedule(
                service_name="transcript_processor",
                initial_inputs={"video_id": video_id},
            )

            # 2. Generate questions
            questions_result = await self.service_orchestrator.schedule(
                service_name="question_generator",
                initial_inputs={"transcript": transcript_result},
            )

            # 3. Generate audio for questions
            audio_results = []
            for question in questions_result["questions"]:
                audio_result = await self.service_orchestrator.schedule(
                    service_name="audio_generator",
                    initial_inputs={"text": question["text"]},
                )
                audio_results.append(audio_result)

            # Track metrics for question generation
            for question in questions_result["questions"]:
                QUESTIONS_GENERATED.labels(
                    difficulty_level=question["difficulty_level"],
                    content_type=question["content_type"],
                ).inc()

            return {
                "success": True,
                "transcript": transcript_result,
                "questions": questions_result["questions"],
                "audio_files": audio_results,
                "analytics": {
                    "video_duration": transcript_result["metadata"]["length"],
                    "question_count": len(questions_result["questions"]),
                    "difficulty_distribution": questions_result["metadata"][
                        "difficulty_distribution"
                    ],
                    "content_types": questions_result["metadata"][
                        "content_types"
                    ],
                },
            }
        except Exception as e:
            logger.error(f"Error in pipeline: {e}")
            raise


if __name__ == "__main__":
    mega_service = KoreanListeningMegaService()
    mega_service.run()
