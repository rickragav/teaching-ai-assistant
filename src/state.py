"""
LangGraph State Schema for English Teacher AI Assistant
"""

from typing import TypedDict, List, Dict, Optional, Annotated
from langgraph.graph import add_messages


class TeachingState(TypedDict):
    """LangGraph state for teaching workflow"""

    # User tracking
    user_id: str

    # Current lesson
    current_lesson_id: int
    lesson_title: str

    # Conversation messages (with LangGraph message handling)
    messages: Annotated[List[Dict[str, str]], add_messages]

    # User input
    user_input: str

    # RAG retrieved content
    retrieved_content: Optional[str]

    # Teaching response
    teacher_response: Optional[str]

    # Raw LLM response object for voice streaming
    llm_response: Optional[object]

    # Phase tracking
    phase: str  # "teaching", "quiz", "evaluation", "completed"

    # Quiz data
    quiz_questions: Optional[List[Dict[str, str]]]
    quiz_answers: Optional[List[str]]
    quiz_score: Optional[float]
    quiz_passed: Optional[bool]

    # Navigation
    next_action: str  # "continue", "quiz", "next_lesson", "exit"

    # Request source (for formatting)
    source: Optional[str]  # "ui", "voice", "cli" - determines response formatting

    # Error handling
    error: Optional[str]
