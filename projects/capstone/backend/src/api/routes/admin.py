from fastapi import APIRouter, HTTPException

# Removed unused Depends, AsyncSession, get_db
from ...db.init_db import reset_all, reset_session

# from ...database import get_db # Not used here

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/reset/all")
async def reset_database():
    """Reset entire database"""
    try:
        reset_all()
        return {"status": "success", "message": "Database fully reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset/session/{session_id}")
async def reset_study_session(session_id: int):
    """Reset specific study session data"""
    try:
        reset_session(session_id)
        return {
            "status": "success",
            "message": f"Session {session_id} reset successful",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
