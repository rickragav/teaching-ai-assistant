"""
RAG Setup Script - Initialize vector store with lesson transcriptions
"""

from pathlib import Path
from .loader import LessonLoader
from .vector_store import LessonVectorStore
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


def setup_rag_system(force_rebuild: bool = False) -> LessonVectorStore:
    """
    Setup or load the RAG system

    Args:
        force_rebuild: If True, delete and rebuild vector store from scratch

    Returns:
        Initialized LessonVectorStore instance
    """
    logger.info("Setting up RAG system...")

    # Initialize components
    loader = LessonLoader()
    vector_store = LessonVectorStore()

    # Check if vector store exists
    chroma_path = Path(vector_store.chroma_path)
    store_exists = chroma_path.exists() and any(chroma_path.iterdir())

    if force_rebuild and store_exists:
        logger.info("Force rebuild requested - deleting existing store")
        vector_store.load_existing_store()
        vector_store.delete_collection()
        store_exists = False

    if not store_exists:
        logger.info("Vector store not found - creating new one")

        # Load all lessons
        all_chunks = loader.load_all_lessons()

        if not all_chunks:
            raise RuntimeError("No lesson files found to initialize RAG system")

        # Initialize vector store
        vector_store.initialize_store(all_chunks)
        logger.info(f"RAG system initialized with {len(all_chunks)} chunks")
    else:
        logger.info("Loading existing vector store")
        vector_store.load_existing_store()
        logger.info("RAG system loaded successfully")

    return vector_store


def test_rag_retrieval(vector_store: LessonVectorStore, query: str, k: int = 3) -> None:
    """
    Test RAG retrieval with a sample query

    Args:
        vector_store: Initialized vector store
        query: Test query
        k: Number of results to retrieve
    """
    logger.info(f"\nTesting RAG retrieval with query: '{query}'")
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"{'='*80}\n")

    results = vector_store.retrieve_relevant_chunks(query, k=k)

    for i, doc in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"  Lesson ID: {doc.metadata.get('lesson_id', 'N/A')}")
        print(f"  Content: {doc.page_content[:200]}...")
        print(f"  Source: {doc.metadata.get('source', 'N/A')}")
        print()


if __name__ == "__main__":
    # Setup RAG system
    vs = setup_rag_system(force_rebuild=False)

    # Run test queries
    test_queries = [
        "What is the present simple tense?",
        "How do I form questions in present continuous?",
        "Tell me about past simple tense",
        "What are the rules for third person singular?",
    ]

    for query in test_queries:
        test_rag_retrieval(vs, query, k=2)
