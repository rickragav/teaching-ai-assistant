"""
FastAPI Application Setup
Run with: uvicorn src.api.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router
from .websocket import websocket_router
from .state import initialize_system
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="LangGraph Teaching API",
    description="Real-time chat interface for English Teacher AI",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)
app.include_router(websocket_router)


@app.on_event("startup")
async def startup_event():
    """Initialize LangGraph system on startup"""
    logger.info("🚀 Starting LangGraph Teaching API...")

    try:
        await initialize_system()
        logger.info("✅ LangGraph system initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down LangGraph Teaching API...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
