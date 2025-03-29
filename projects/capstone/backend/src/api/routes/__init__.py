from .words import router as words_router
from .groups import router as groups_router
from .study_sessions import router as sessions_router
from .activity_logs import router as logs_router
from .mistakes import router as mistakes_router
from .dashboard import router as dashboard_router

__all__ = [
    "words_router",
    "groups_router",
    "sessions_router",
    "logs_router",
    "mistakes_router",
    "dashboard_router",
]
