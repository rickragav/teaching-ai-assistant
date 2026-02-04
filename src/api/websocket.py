"""
WebSocket Handler for Real-time Chat
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json

from .state import get_teaching_graph, get_lesson_metadata
from ..database.progress import get_or_create_user, get_current_lesson_id, save_message, get_conversation_history
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

websocket_router = APIRouter()

# Active WebSocket connections
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
    """Handle user initialization"""
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
    
    await websocket.send_json({
        "type": "user_created",
        "user_id": user_id,
        "current_lesson_id": lesson_id,
        "lesson_title": lesson_info["title"],
        "conversation_history": history,  # Send previous messages
        "completed_lessons": completed_lessons  # Send for progress bar
    })


async def handle_message(websocket: WebSocket, message_data: dict):
    """Handle teaching interaction"""
    user_input = message_data["message"]
    user_id = message_data["user_id"]
    lesson_id = message_data.get("lesson_id", 1)
    
    # Get lesson info
    lesson_metadata = get_lesson_metadata()
    lesson_info = lesson_metadata.get(lesson_id, {"title": f"Lesson {lesson_id}"})
    
    # Show thinking indicator
    await websocket.send_json({"type": "thinking"})
    
    # Prepare state
    state = {
        "user_id": user_id,
        "current_lesson_id": lesson_id,
        "lesson_title": lesson_info["title"],
        "messages": [],
        "user_input": user_input,
        "phase": "teaching",
        "next_action": "quiz" if "quiz" in user_input.lower() else "continue",
        "source": "ui"  # Flag to indicate UI request for markdown formatting
    }
    
    try:
        # Save user message
        save_message(user_id, "user", user_input)
        
        # Run through LangGraph
        teaching_graph = get_teaching_graph()
        result = teaching_graph.run(state)
        
        # Send response
        response_text = result.get("teacher_response", "I'm processing your request...")
        
        # Save assistant response
        save_message(user_id, "assistant", response_text)
        
        await websocket.send_json({
            "type": "response",
            "message": response_text
        })
        
        # Update lesson if changed
        new_lesson_id = get_current_lesson_id(user_id)
        if new_lesson_id != lesson_id:
            new_lesson_info = lesson_metadata.get(new_lesson_id, {"title": f"Lesson {new_lesson_id}"})
            await websocket.send_json({
                "type": "lesson_update",
                "lesson_id": new_lesson_id,
                "lesson_title": new_lesson_info["title"]
            })
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
