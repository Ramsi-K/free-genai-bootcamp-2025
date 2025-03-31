from sqlmodel import SQLModel

# Import associations first since others depend on it
from .associations import word_group_map
from .word import Word
from .group import WordGroup
from .activity_log import ActivityLog
from .session_stats import SessionStats
from .study_session import StudySession
from .word_stats import WordStats
from .wrong_input import WrongInput
from .word_review_item import WordReviewItem
from .sample_sentence import SampleSentence

# Update export order
__all__ = [
    "word_group_map",  # Export association tables first
    "Word",
    "WordGroup",
    "ActivityLog",
    "SessionStats",
    "StudySession",
    "WordStats",
    "WrongInput",
    "WordReviewItem",
    "SampleSentence",
]
