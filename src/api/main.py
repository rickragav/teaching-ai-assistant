"""
FastAPI Application for AI English Teacher - LangGraph Backend
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router
from .websocket import websocket_router
from .admin import router as admin_router
from .state import initialize_system
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="AI English Teacher API",
        description="Backend API for Flutter mobile app - LangGraph powered",
        version="1.0.0",
    )

    # CORS configuration for Flutter mobile app
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(router, prefix="/api", tags=["core"])
    app.include_router(admin_router, prefix="/api", tags=["admin"])
    app.include_router(websocket_router, tags=["websocket"])

    # Startup event
    @app.on_event("startup")
    async def on_startup():
        logger.info("🚀 Initializing AI English Teacher API...")
        try:
            await initialize_system()
            logger.info("✅ System initialized successfully")
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise

    # Shutdown event
    @app.on_event("shutdown")
    async def on_shutdown():
        logger.info("👋 Shutting down API...")

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
