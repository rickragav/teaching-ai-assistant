"""
Global state management for API
"""

from typing import Dict, Optional
from ..workflow import TeachingGraph
from ..rag.setup import setup_rag_system
from ..rag.loader import LessonLoader
from ..rag.vector_store import LessonVectorStore
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

# Global instances
_vector_store: Optional[LessonVectorStore] = None
_teaching_graph: Optional[TeachingGraph] = None
_lesson_loader: Optional[LessonLoader] = None
_lesson_metadata: Optional[Dict] = None


async def initialize_system():
    """Initialize LangGraph system"""
    global _vector_store, _teaching_graph, _lesson_loader, _lesson_metadata
    
    _vector_store = setup_rag_system()
    _teaching_graph = TeachingGraph(_vector_store)
    _lesson_loader = LessonLoader()
    _lesson_metadata = _lesson_loader.get_lesson_metadata()


def get_teaching_graph() -> TeachingGraph:
    """Get teaching graph instance"""
    if _teaching_graph is None:
        raise RuntimeError("System not initialized. Call initialize_system() first.")
    return _teaching_graph


def get_lesson_metadata() -> Dict:
    """Get lesson metadata"""
    if _lesson_metadata is None:
        raise RuntimeError("System not initialized. Call initialize_system() first.")
    return _lesson_metadata


def get_vector_store() -> LessonVectorStore:
    """Get vector store instance"""
    if _vector_store is None:
        raise RuntimeError("System not initialized. Call initialize_system() first.")
    return _vector_store
