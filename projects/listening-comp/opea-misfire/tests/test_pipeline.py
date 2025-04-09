import requests
import time
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PipelineTester:
    def __init__(self):
        self.mega_service_url = "http://localhost:8000"
        self.test_video_url = (
            "https://www.youtube.com/watch?v=your_test_video_id"
        )

    def test_health_endpoints(self) -> Dict[str, bool]:
        """Test health endpoints of all services"""
        services = {
            "mega-service": "8000",
            "transcript-processor": "5000",
            "question-module": "5001",
            "audio-module": "5002",
            "embedding": "8080",
            "vector-storage": "5003",
        }

        results = {}
        for service, port in services.items():
            try:
                response = requests.get(f"http://localhost:{port}/health")
                results[service] = response.status_code == 200
                logger.info(
                    f"{service}: {'OK' if results[service] else 'FAILED'}"
                )
            except Exception as e:
                results[service] = False
                logger.error(f"{service} health check failed: {e}")

        return results

    async def test_full_pipeline(self) -> Dict[str, Any]:
        """Test the complete pipeline"""
        try:
            # 1. Process video
            response = requests.post(
                f"{self.mega_service_url}/api/process",
                json={"url": self.test_video_url},
            )
            video_data = response.json()
            video_id = video_data["video_id"]

            # 2. Wait for processing
            time.sleep(5)

            # 3. Check generated questions
            questions_response = requests.get(
                f"{self.mega_service_url}/api/questions/{video_id}"
            )

            # 4. Check audio generation
            audio_response = requests.get(
                f"{self.mega_service_url}/api/audio-questions/{video_id}"
            )

            return {
                "success": True,
                "video_processed": video_data["success"],
                "questions_generated": questions_response.status_code == 200,
                "audio_generated": audio_response.status_code == 200,
                "metrics": self.check_metrics(),
            }

        except Exception as e:
            logger.error(f"Pipeline test failed: {e}")
            return {"success": False, "error": str(e)}

    def check_metrics(self) -> Dict[str, Any]:
        """Verify metrics are being collected"""
        try:
            metrics_response = requests.get(
                "http://localhost:9090/api/v1/query",
                params={"query": "korean_questions_total"},
            )
            return metrics_response.json()
        except Exception as e:
            logger.error(f"Metrics check failed: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    tester = PipelineTester()
    health_results = tester.test_health_endpoints()
    pipeline_results = await tester.test_full_pipeline()
    print("Health Check Results:", health_results)
    print("Pipeline Test Results:", pipeline_results)
