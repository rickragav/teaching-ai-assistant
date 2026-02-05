"""
WebSocket Handler for Chat
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json

from .state import get_teaching_graph, get_lesson_metadata
from ..database.progress import (
    get_or_create_user,
    get_current_lesson_id,
    save_message,
    get_conversation_history,
)
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

# Initialize router
websocket_router = APIRouter()


active_connections: Dict[str, WebSocket] = {}
active_connections: Dict[str, WebSocket] = {}


@websocket_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    connection_id = id(websocket)
    active_connections[connection_id] = websocket

    logger.info(f"WebSocket connection established: {connection_id}")

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            logger.info(f"Received: {message_data.get('type', 'unknown')}")

            if message_data["type"] == "init":
                await handle_init(websocket, message_data)
            elif message_data["type"] == "message":
                await handle_message(websocket, message_data)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
        if connection_id in active_connections:
            del active_connections[connection_id]
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if connection_id in active_connections:
            del active_connections[connection_id]


async def handle_init(websocket: WebSocket, message_data: dict):
    """Handle user initialization and send greeting"""
    user_id = message_data["user_id"]
    user = get_or_create_user(user_id)
    lesson_id = user["current_lesson_id"]

    # Get lesson info
    lesson_metadata = get_lesson_metadata()
    lesson_info = lesson_metadata.get(lesson_id, {"title": f"Lesson {lesson_id}"})

    # Get conversation history
    history = get_conversation_history(user_id)

    # Get progress info
    completed_lessons = user.get("completed_lessons", [])

    await websocket.send_json(
        {
            "type": "user_created",
            "user_id": user_id,
            "current_lesson_id": lesson_id,
            "lesson_title": lesson_info["title"],
            "conversation_history": history,  # Send previous messages
            "completed_lessons": completed_lessons,  # Send for progress bar
        }
    )

    # Generate and send greeting automatically
    logger.info(f"Generating greeting for user {user_id}...")
    await websocket.send_json({"type": "thinking"})

    try:
        # Get teaching graph
        graph = get_teaching_graph()

        # Prepare state with __greeting__ flag
        # Convert history format: sender/text -> role/content
        formatted_history = []
        for msg in history:
            formatted_history.append(
                {
                    "role": msg.get("sender", "user"),  # sender: 'user' or 'assistant'
                    "content": msg.get("text", ""),
                }
            )

        state = {
            "user_id": user_id,
            "current_lesson_id": lesson_id,
            "lesson_title": lesson_info["title"],
            "messages": formatted_history,
            "user_input": "__greeting__",  # Special flag for greeting
        }

        # Run graph to generate greeting
        greeting_sent = False
        async for event in graph.astream(state):
            if greeting_sent:
                # Skip remaining events after greeting is sent
                continue

            for node_name, node_output in event.items():
                # Only process greeting node output, ignore other nodes
                if (
                    node_name == "greeting"
                    and isinstance(node_output, dict)
                    and "teacher_response" in node_output
                ):
                    greeting_text = node_output["teacher_response"]

                    # Send greeting as AI message
                    await websocket.send_json(
                        {
                            "type": "response",
                            "message": greeting_text,
                            "is_greeting": True,
                        }
                    )

                    # Save greeting to conversation history
                    save_message(user_id, "assistant", greeting_text)
                    logger.info(f"Greeting sent to user {user_id}")
                    # Mark as sent to skip remaining events
                    greeting_sent = True
                    break

    except Exception as e:
        logger.error(f"Error generating greeting: {e}")
        # Send fallback greeting
        fallback_greeting = f"Hello! Welcome to {lesson_info['title']}. I'm excited to help you improve your English skills today!"
        await websocket.send_json(
            {
                "type": "response",
                "message": fallback_greeting,
                "is_greeting": True,
            }
        )
        save_message(user_id, "assistant", fallback_greeting)


async def handle_message(websocket: WebSocket, message_data: dict):
    """Handle text chat messages"""
    user_input = message_data["message"]
    user_id = message_data["user_id"]
    lesson_id = message_data.get("lesson_id", 1)

    # Get lesson info
    lesson_metadata = get_lesson_metadata()
    lesson_info = lesson_metadata.get(lesson_id, {"title": f"Lesson {lesson_id}"})

    # Show thinking indicator
    await websocket.send_json({"type": "thinking"})

    # Get conversation history to maintain context
    history = get_conversation_history(user_id)

    # Convert history format: sender/text -> role/content
    formatted_history = []
    for msg in history:
        formatted_history.append(
            {
                "role": msg.get("sender", "user"),  # sender: 'user' or 'assistant'
                "content": msg.get("text", ""),
            }
        )

    # Detect quiz intent from user input
    quiz_triggers = [
        "quiz",
        "test me",
        "yes",
        "sure",
        "ok",
        "okay",
        "let's do it",
        "ready",
    ]
    user_wants_quiz = any(trigger in user_input.lower() for trigger in quiz_triggers)

    # Check if previous message was offering a quiz
    offering_quiz = False
    if formatted_history:
        last_assistant_msg = None
        for msg in reversed(formatted_history):
            if msg.get("role") == "assistant":
                last_assistant_msg = msg.get("content", "").lower()
                break
        if last_assistant_msg and (
            "quiz" in last_assistant_msg or "test your knowledge" in last_assistant_msg
        ):
            offering_quiz = True

    # Determine next action
    next_action = "continue"
    if user_wants_quiz and offering_quiz:
        next_action = "quiz"
        logger.info(f"Quiz intent detected: user agreed to quiz offer")

    # Prepare state for LangGraph
    state = {
        "user_id": user_id,
        "current_lesson_id": lesson_id,
        "lesson_title": lesson_info["title"],
        "messages": formatted_history,
        "user_input": user_input,
        "phase": "teaching",
        "next_action": next_action,
        "source": "ui",
    }

    logger.info(
        f"Processing message from {user_id}: '{user_input}' (lesson: {lesson_id}, history: {len(formatted_history)} messages)"
    )

    try:
        # Save user message
        save_message(user_id, "user", user_input)

        # Run through LangGraph with streaming
        teaching_graph = get_teaching_graph()

        response_text = None
        event_count = 0
        async for event in teaching_graph.astream(state):
            event_count += 1
            logger.info(f"Stream event #{event_count}: {list(event.keys())}")

            for node_name, node_output in event.items():
                logger.info(
                    f"Node '{node_name}' output type: {type(node_output)}, keys: {list(node_output.keys()) if isinstance(node_output, dict) else 'N/A'}"
                )

                if isinstance(node_output, dict):
                    if "teacher_response" in node_output:
                        response_text = node_output["teacher_response"]
                        logger.info(
                            f"✓ Found teacher_response: {response_text[:100]}..."
                        )

                        # Send response
                        await websocket.send_json(
                            {"type": "response", "message": response_text}
                        )
                    else:
                        logger.warning(
                            f"Node output missing 'teacher_response'. Available keys: {list(node_output.keys())}"
                        )

        logger.info(
            f"Streaming completed. Total events: {event_count}, Response found: {response_text is not None}"
        )

        # Fallback if no response was generated
        if not response_text:
            logger.error("No response generated from graph, using fallback")
            response_text = "I'm processing your request..."
            await websocket.send_json({"type": "response", "message": response_text})

        # Save assistant response
        save_message(user_id, "assistant", response_text)

        # Update lesson if changed
        new_lesson_id = get_current_lesson_id(user_id)
        if new_lesson_id != lesson_id:
            new_lesson_info = lesson_metadata.get(
                new_lesson_id, {"title": f"Lesson {new_lesson_id}"}
            )
            await websocket.send_json(
                {
                    "type": "lesson_update",
                    "lesson_id": new_lesson_id,
                    "lesson_title": new_lesson_info["title"],
                }
            )

    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        await websocket.send_json({"type": "error", "message": str(e)})
