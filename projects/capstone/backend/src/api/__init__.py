from fastapi import APIRouter
from .routes import (
    words,
    groups,
    study_sessions,
    study_activities,
    dashboard,
    admin,
)

router = APIRouter()

router.include_router(words.router, prefix="/words", tags=["words"])
router.include_router(groups.router, prefix="/groups", tags=["groups"])
router.include_router(
    study_sessions.router, prefix="/study_sessions", tags=["study_sessions"]
)
router.include_router(
    study_activities.router,
    prefix="/study_activities",
    tags=["study_activities"],
)
router.include_router(
    dashboard.router, prefix="/dashboard", tags=["dashboard"]
)
router.include_router(admin.router, prefix="/admin", tags=["admin"])
