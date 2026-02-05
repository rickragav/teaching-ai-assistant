"""
REST API Routes for Flutter Mobile App
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import re
import os
from pathlib import Path

from .state import get_lesson_metadata
from ..database.progress import (
    get_or_create_user,
    register_user,
    authenticate_user,
    update_user_mode,
)
from ..database.connection import db
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


# Response Models
class HealthResponse(BaseModel):
    status: str
    graph_initialized: bool
    lessons_loaded: int


class LessonInfo(BaseModel):
    id: str
    title: str


class LessonsResponse(BaseModel):
    lessons: list[LessonInfo]


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    phone_number: str = Field(..., min_length=10, max_length=10)

    @validator("name")
    def validate_name(cls, v):
        # Remove extra spaces and validate
        v = " ".join(v.split())
        if not re.match(r"^[a-zA-Z\s]+$", v):
            raise ValueError("Name can only contain letters and spaces")
        return v

    @validator("phone_number")
    def validate_phone(cls, v):
        # Remove any non-digit characters
        v = re.sub(r"\D", "", v)
        if len(v) != 10:
            raise ValueError("Phone number must be exactly 10 digits")
        if v[0] in ["0", "1"]:
            raise ValueError("Phone number must start with digits 2-9")
        return v


class LoginRequest(BaseModel):
    name: str
    phone_number: str


class AuthResponse(BaseModel):
    user_id: str
    name: str
    phone_number: str
    selected_mode: Optional[str] = None
    message: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        metadata = get_lesson_metadata()
        return HealthResponse(
            status="healthy",
            graph_initialized=True,
            lessons_loaded=len(metadata),
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            graph_initialized=False,
            lessons_loaded=0,
        )


class OnlineStatusResponse(BaseModel):
    online: bool
    message: str


@router.get("/agent/status", response_model=OnlineStatusResponse)
async def get_agent_status():
    """Check if AI agent is online and available"""
    try:
        # Check if OpenAI API key is configured
        import os

        has_api_key = bool(os.getenv("OPENAI_API_KEY"))

        if has_api_key:
            return OnlineStatusResponse(
                online=True, message="AI Teacher is online and ready to help!"
            )
        else:
            return OnlineStatusResponse(
                online=False,
                message="AI Teacher is currently offline - API key not configured",
            )
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return OnlineStatusResponse(online=False, message="Unable to determine status")


@router.get("/lessons", response_model=LessonsResponse)
async def get_lessons():
    """Get all available lessons for Flutter app"""
    try:
        metadata = get_lesson_metadata()
        lessons = [
            LessonInfo(id=lesson_id, title=info["title"])
            for lesson_id, info in metadata.items()
        ]
        return LessonsResponse(lessons=lessons)
    except Exception as e:
        logger.error(f"Failed to fetch lessons: {e}")
        raise HTTPException(status_code=503, detail="Failed to load lessons")


@router.post("/auth/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register a new user with name and phone number"""
    try:
        user_id = f"user_{request.phone_number}"

        # Check if user already exists
        existing_user = authenticate_user(request.name, request.phone_number)
        if existing_user:
            logger.info(f"User already exists: {user_id}")
            raise HTTPException(
                status_code=400,
                detail="User with this phone number already exists. Please login.",
            )

        # Register new user
        user_data = register_user(
            user_id=user_id, name=request.name, phone_number=request.phone_number
        )

        logger.info(f"Registered new user: {user_id}")
        return AuthResponse(
            user_id=user_data["user_id"],
            name=user_data["name"],
            phone_number=user_data["phone_number"],
            selected_mode=user_data.get("selected_mode"),
            message="Registration successful",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login user with name and phone number"""
    try:
        user_data = authenticate_user(request.name, request.phone_number)

        if not user_data:
            # Auto-register if user doesn't exist (simplified login)
            user_id = f"user_{request.phone_number}"
            user_data = register_user(
                user_id=user_id, name=request.name, phone_number=request.phone_number
            )
            logger.info(f"Auto-registered user during login: {user_id}")
        else:
            logger.info(f"User logged in: {user_data['user_id']}")

        return AuthResponse(
            user_id=user_data["user_id"],
            name=user_data["name"],
            phone_number=user_data["phone_number"],
            selected_mode=user_data.get("selected_mode"),
            message="Login successful",
        )
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.get("/user/{user_id}")
async def get_user_progress(user_id: str):
    """Get user progress and history"""
    try:
        user = get_or_create_user(user_id)
        return user
    except Exception as e:
        logger.error(f"Failed to fetch user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user data")


class UpdateModeRequest(BaseModel):
    mode: str = Field(..., pattern="^(chat|voice)$")


@router.patch("/users/{user_id}/mode")
async def update_mode(user_id: str, request: UpdateModeRequest):
    """Update user's selected learning mode"""
    try:
        user_data = update_user_mode(user_id, request.mode)

        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"Updated mode for user {user_id}: {request.mode}")
        return {
            "user_id": user_data["user_id"],
            "selected_mode": user_data["selected_mode"],
            "message": "Mode updated successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update mode for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update mode")


# Learning Path Models
class LessonNode(BaseModel):
    id: str
    title: str
    subtitle: str
    section: str
    order: int
    is_completed: bool = False
    is_locked: bool = False
    is_current: bool = False
    progress: float = 0.0


class SectionInfo(BaseModel):
    id: str
    title: str
    lessons: List[LessonNode]


class LearningPathResponse(BaseModel):
    user_id: str
    sections: List[SectionInfo]
    stats: dict


@router.get("/learning-path/{user_id}", response_model=LearningPathResponse)
async def get_learning_path(user_id: str):
    """Get user's learning path with progress from JSON database"""
    try:
        # Get courses from JSON database
        courses = db.get_all_courses()

        if not courses:
            logger.warning("No courses found in database")
            return LearningPathResponse(
                user_id=user_id,
                sections=[],
                stats={
                    "total_lessons": 0,
                    "completed_lessons": 0,
                    "streak_days": 0,
                    "total_points": 0,
                }
            )

        sections_data = []
        total_lessons = 0
        completed_lessons = 0

        # Get user progress
        user = get_or_create_user(user_id)
        completed_lesson_ids = user.get("completed_lessons", [])

        # Iterate through courses
        for course_id, course_data in courses.items():
            if course_data.get("status") != "published":
                continue

            course_title = course_data.get("title", "")
            sections = course_data.get("sections", [])

            # Iterate through sections
            for section in sections:
                section_id = section.get("id", "")
                section_title = section.get("title", "")
                lessons = section.get("lessons", [])

                lesson_nodes = []

                for idx, lesson in enumerate(lessons):
                    lesson_id = lesson.get("id", "")
                    lesson_title = lesson.get("title", "")
                    lesson_subtitle = lesson.get("subtitle", section_title)

                    # Determine lesson status
                    is_completed = lesson_id in completed_lesson_ids
                    is_current = total_lessons == 0 and not is_completed
                    is_locked = total_lessons > 0 and not is_completed

                    lesson_nodes.append(
                        LessonNode(
                            id=lesson_id,
                            title=lesson_title,
                            subtitle=lesson_subtitle,
                            section=section_id,
                            order=idx + 1,
                            is_completed=is_completed,
                            is_locked=is_locked,
                            is_current=is_current,
                            progress=1.0 if is_completed else 0.0,
                        )
                    )

                    total_lessons += 1
                    if is_completed:
                        completed_lessons += 1

                if lesson_nodes:
                    sections_data.append(
                        SectionInfo(
                            id=section_id,
                            title=f"{course_title} - {section_title}",
                            lessons=lesson_nodes,
                        )
                    )

        # Calculate stats
        stats = {
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "streak_days": 0,  # TODO: Calculate from database
            "total_points": 0,  # TODO: Calculate from database
        }

        logger.info(
            f"Retrieved learning path for user {user_id}: {total_lessons} lessons"
        )

        return LearningPathResponse(
            user_id=user_id, sections=sections_data, stats=stats
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get learning path for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve learning path")
        raise HTTPException(status_code=500, detail="Failed to update mode")
