"""Schema imports with proper forward references"""

# Base schemas (no dependencies)
from .word import WordBase, WordCreate, WordUpdate
from .group import GroupCreate
from .activity_log import ActivityLogBase, ActivityLogCreate
from .sample_sentence import SampleSentenceBase, SampleSentenceCreate
from .word_stats import WordStatsBase, WordStatsCreate, WordStatsUpdate
from .session_stats import SessionStatsBase, SessionStatsCreate
from .wrong_input import WrongInputBase, WrongInputCreate

# Response schemas (with dependencies)
from .word import WordResponse
from .group import GroupResponse
from .activity_log import ActivityLogResponse
from .sample_sentence import SampleSentenceResponse
from .word_stats import WordStatsResponse
from .session_stats import SessionStatsResponse
from .wrong_input import WrongInputResponse

__all__ = [
    # Base schemas
    "WordBase",
    "WordCreate",
    "WordUpdate",
    "GroupCreate",
    "ActivityLogBase",
    "ActivityLogCreate",
    "SampleSentenceBase",
    "SampleSentenceCreate",
    "WordStatsBase",
    "WordStatsCreate",
    "WordStatsUpdate",
    "SessionStatsBase",
    "SessionStatsCreate",
    "WrongInputBase",
    "WrongInputCreate",
    # Response schemas
    "WordResponse",
    "GroupResponse",
    "ActivityLogResponse",
    "SampleSentenceResponse",
    "WordStatsResponse",
    "SessionStatsResponse",
    "WrongInputResponse",
]
