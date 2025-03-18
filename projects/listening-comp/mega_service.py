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
            endpoint="/api/process-video",
            service_type=ServiceType.PROCESSOR,
            role_type=ServiceRoleType.PROCESSOR,
        )

        # Embedding service
        self.embedding_service = MicroService(
            name="embedding",
            host="tei-embedding",
            port=8080,
            endpoint="/embed",
            service_type=ServiceType.EMBEDDING,
            role_type=ServiceRoleType.ENCODER,
        )

        # Vector storage service (using ChromaDB internally)
        self.vector_storage = MicroService(
            name="vector_storage",
            host="question-module",
            port=5001,
            endpoint="/api/store-vectors",
            service_type=ServiceType.STORAGE,
            role_type=ServiceRoleType.STORAGE,
        )

        # Question generation service
        self.question_gen = MicroService(
            name="question_generator",
            host="question-module",
            port=5001,
            endpoint="/api/generate-questions",
            service_type=ServiceType.LLM,
            role_type=ServiceRoleType.GENERATOR,
        )

        # Text-to-speech service
        self.tts_service = MicroService(
            name="tts",
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

        # Register all services
        for service in [
            self.transcript_service,
            self.embedding_service,
            self.vector_storage,
            self.question_gen,
            self.tts_service,
            self.llm_service,
        ]:
            self.service_orchestrator.add(service)

    async def process_request(self, request_data):
        """
        Main processing pipeline:
        1. Get YouTube transcript
        2. Create embeddings
        3. Store in vector DB
        4. Generate questions
        5. Convert to speech
        """
        try:
            video_id = request_data.get("video_id")
            if not video_id:
                raise ValueError("No video ID provided")

            # Process transcript
            transcript_result = await self.service_orchestrator.schedule(
                service_name="transcript_processor",
                initial_inputs={"video_id": video_id},
            )

            # Create embeddings and store
            embedding_result = await self.service_orchestrator.schedule(
                service_name="embedding",
                initial_inputs={"text": transcript_result["text"]},
            )

            await self.service_orchestrator.schedule(
                service_name="vector_storage",
                initial_inputs={
                    "embeddings": embedding_result["embeddings"],
                    "text": transcript_result["text"],
                },
            )

            # Generate questions
            questions_result = await self.service_orchestrator.schedule(
                service_name="question_generator",
                initial_inputs={"text": transcript_result["text"]},
            )

            # Generate audio for questions
            audio_results = []
            for question in questions_result["questions"]:
                audio_result = await self.service_orchestrator.schedule(
                    service_name="tts",
                    initial_inputs={"text": question["text"]},
                )
                audio_results.append(audio_result)

            return {
                "success": True,
                "questions": questions_result["questions"],
                "audio_files": audio_results,
            }

        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    mega_service = KoreanListeningMegaService()
    mega_service.run()
