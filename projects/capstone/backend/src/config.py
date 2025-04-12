import os
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Database configurations
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "/app/data/hagxwon.db")
print(f"Using database at: {SQLITE_DB_PATH}")
VECTOR_DB_PATH = str(PROJECT_ROOT / "database" / "vector_store")

# Model configurations
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
LLM_MODEL = "gpt-3.5-turbo"

# Agent configurations
AGENT_ROLES = {
    "teacher": {
        "description": "Educational content expert",
        "temperature": 0.3,
    },
    "student_assistant": {
        "description": "Helps with student queries",
        "temperature": 0.5,
    },
    "content_curator": {
        "description": "Manages and organizes educational content",
        "temperature": 0.2,
    },
}
