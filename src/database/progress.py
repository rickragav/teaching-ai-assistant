"""
Simple CRUD operations for user progress using JSON storage
"""

from datetime import datetime
from typing import Dict
from .connection import db
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


def get_or_create_user(user_id: str) -> Dict:
    """
    Get user progress or create new user

    Args:
        user_id: User identifier

    Returns:
        Dict with user progress data
    """
    user_data = db.get_user(user_id)

    if user_data:
        logger.info(f"Found existing user: {user_id}")
        return user_data

    # Create new user
    logger.info(f"Creating new user: {user_id}")
    now = datetime.now().isoformat()

    user_data = {
        "user_id": user_id,
        "current_lesson_id": 1,
        "completed_lessons": [],
        "lesson_scores": {},
        "conversation_history": [],  # Store chat messages
        "last_accessed": now,
        "created_at": now,
    }

    db.save_user(user_id, user_data)
    return user_data


def update_progress(user_id: str, lesson_id: int, score: float, passed: bool) -> None:
    """
    Update user progress after quiz

    Args:
        user_id: User identifier
        lesson_id: Completed lesson ID
        score: Quiz score (0.0-1.0)
        passed: Whether user passed the quiz
    """
    user = get_or_create_user(user_id)

    # Update lesson scores
    user["lesson_scores"][str(lesson_id)] = score

    # Update completed lessons and advance if passed
    if passed and lesson_id not in user["completed_lessons"]:
        user["completed_lessons"].append(lesson_id)
        user["current_lesson_id"] = lesson_id + 1
    else:
        user["current_lesson_id"] = lesson_id  # Stay on same lesson if failed

    user["last_accessed"] = datetime.now().isoformat()

    # Save updated user data
    db.save_user(user_id, user)

    logger.info(
        f"Updated progress for user {user_id}: Lesson {lesson_id}, Score {score:.2f}, Passed: {passed}"
    )


def get_current_lesson_id(user_id: str) -> int:
    """
    Get user's current lesson ID

    Args:
        user_id: User identifier

    Returns:
        Current lesson ID
    """
    user = get_or_create_user(user_id)
    return user["current_lesson_id"]


def save_message(user_id: str, sender: str, text: str) -> None:
    """
    Save a message to user's conversation history

    Args:
        user_id: User identifier
        sender: Message sender ('user' or 'assistant')
        text: Message text
    """
    user = get_or_create_user(user_id)

    # Initialize conversation_history if not exists (for existing users)
    if "conversation_history" not in user:
        user["conversation_history"] = []

    # Add message with timestamp
    message = {"sender": sender, "text": text, "timestamp": datetime.now().isoformat()}

    user["conversation_history"].append(message)
    user["last_accessed"] = datetime.now().isoformat()

    # Keep only last 100 messages to prevent database bloat
    if len(user["conversation_history"]) > 100:
        user["conversation_history"] = user["conversation_history"][-100:]

    db.save_user(user_id, user)
    logger.info(f"Saved message for user {user_id}: {sender}")


def get_conversation_history(user_id: str) -> list:
    """
    Get user's conversation history

    Args:
        user_id: User identifier

    Returns:
        List of message dictionaries
    """
    user = get_or_create_user(user_id)
    return user.get("conversation_history", [])


def register_user(user_id: str, name: str, phone_number: str) -> Dict:
    """
    Register a new user with name and phone number

    Args:
        user_id: User identifier (usually user_{phone_number})
        name: User's name
        phone_number: User's phone number (10 digits)

    Returns:
        Dict with user data
    """
    # Check if user already exists
    existing_user = db.get_user(user_id)
    if existing_user:
        logger.warning(f"User already exists: {user_id}")
        return existing_user

    now = datetime.now().isoformat()

    user_data = {
        "user_id": user_id,
        "name": name,
        "phone_number": phone_number,
        "selected_mode": None,  # 'chat' or 'voice'
        "current_lesson_id": 1,
        "completed_lessons": [],
        "lesson_scores": {},
        "conversation_history": [],
        "last_accessed": now,
        "created_at": now,
    }

    db.save_user(user_id, user_data)
    logger.info(f"Registered new user: {user_id} ({name})")
    return user_data


def authenticate_user(name: str, phone_number: str) -> Dict | None:
    """
    Authenticate user by name and phone number

    Args:
        name: User's name
        phone_number: User's phone number

    Returns:
        User data dict if found and matches, None otherwise
    """
    user_id = f"user_{phone_number}"
    user_data = db.get_user(user_id)

    if not user_data:
        logger.info(f"User not found: {user_id}")
        return None

    # Verify name matches (case-insensitive)
    if user_data.get("name", "").lower() != name.lower():
        logger.warning(f"Name mismatch for user {user_id}")
        return None

    # Update last accessed
    user_data["last_accessed"] = datetime.now().isoformat()
    db.save_user(user_id, user_data)

    logger.info(f"User authenticated: {user_id} ({name})")
    return user_data


def update_user_mode(user_id: str, mode: str) -> Dict | None:
    """
    Update user's selected learning mode

    Args:
        user_id: User identifier
        mode: Selected mode ('chat' or 'voice')

    Returns:
        Updated user data dict if successful, None otherwise
    """
    user_data = db.get_user(user_id)

    if not user_data:
        logger.warning(f"User not found: {user_id}")
        return None

    # Update selected mode
    user_data["selected_mode"] = mode
    user_data["last_accessed"] = datetime.now().isoformat()
    db.save_user(user_id, user_data)

    logger.info(f"Updated mode for user {user_id}: {mode}")
    return user_data
