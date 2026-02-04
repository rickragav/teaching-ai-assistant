"""
REST API Routes
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from .state import get_lesson_metadata
from .templates import get_chat_html
from ..database.progress import get_or_create_user
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    """Serve the chat interface HTML"""
    return get_chat_html()


@router.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        metadata = get_lesson_metadata()
        return {
            "status": "healthy",
            "graph_initialized": True,
            "lessons_loaded": len(metadata),
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@router.get("/api/lessons")
async def get_lessons():
    """Get all available lessons"""
    try:
        lesson_metadata = get_lesson_metadata()
        return {
            "lessons": [
                {"id": lesson_id, "title": info["title"]}
                for lesson_id, info in lesson_metadata.items()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/api/user/{user_id}")
async def get_user_progress(user_id: str):
    """Get user progress"""
    try:
        user = get_or_create_user(user_id)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
