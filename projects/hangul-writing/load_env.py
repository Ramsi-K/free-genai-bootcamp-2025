"""
Simple script to load environment variables from .env file
"""

import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


def load_environment_variables():
    """Load environment variables from .env file if it exists"""
    env_path = os.path.join(os.path.dirname(__file__), ".env")

    if os.path.exists(env_path):
        logger.info(f"Loading environment variables from {env_path}")
        load_dotenv(env_path)

        # Check if critical API keys are present
        imgbb_key = os.environ.get("IMGBB_API_KEY")
        hf_key = os.environ.get("HF_API_KEY")

        if imgbb_key and hf_key:
            logger.info("✅ API keys loaded successfully")
            logger.info("Using HuggingFace Inference API for LLaVA model")
        else:
            logger.warning(
                "⚠️ API keys not found, will use local model if possible"
            )

        return True
    else:
        logger.warning(
            "No .env file found, using default environment variables"
        )
        return False


if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Load environment variables
    load_environment_variables()
