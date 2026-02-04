"""
RAG Vector Store - ChromaDB operations for lesson embeddings
"""

from typing import List, Optional
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from ..config import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class LessonVectorStore:
    """Manage ChromaDB vector store for lesson content"""

    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key, model="text-embedding-3-small"
        )
        self.chroma_path = str(settings.chroma_path)
        self.collection_name = "lesson_transcriptions"
        self._vector_store = None

    def initialize_store(self, documents: List[Document]) -> None:
        """
        Initialize or recreate the vector store with documents

        Args:
            documents: List of Document objects to embed and store
        """
        logger.info(f"Initializing vector store with {len(documents)} documents")

        self._vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=self.chroma_path,
        )

        logger.info(f"Vector store initialized at {self.chroma_path}")

    def load_existing_store(self) -> None:
        """Load existing vector store from disk"""
        logger.info(f"Loading existing vector store from {self.chroma_path}")

        self._vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.chroma_path,
        )

        logger.info("Existing vector store loaded successfully")

    def add_documents(self, documents: List[Document]) -> None:
        """
        Add new documents to existing vector store

        Args:
            documents: List of Document objects to add
        """
        if self._vector_store is None:
            logger.error("Vector store not initialized. Call initialize_store() first.")
            raise RuntimeError("Vector store not initialized")

        logger.info(f"Adding {len(documents)} documents to vector store")
        self._vector_store.add_documents(documents)
        logger.info("Documents added successfully")

    def retrieve_relevant_chunks(
        self, query: str, k: int = None, lesson_id: Optional[int] = None
    ) -> List[Document]:
        """
        Retrieve relevant chunks for a query

        Args:
            query: User's question or topic
            k: Number of chunks to retrieve (defaults to settings.retrieval_k)
            lesson_id: Optional filter to retrieve only from specific lesson

        Returns:
            List of relevant Document chunks
        """
        if self._vector_store is None:
            logger.error(
                "Vector store not initialized. Call load_existing_store() first."
            )
            raise RuntimeError("Vector store not initialized")

        k = k or settings.retrieval_k

        # Build filter if lesson_id specified
        filter_dict = None
        if lesson_id is not None:
            filter_dict = {"lesson_id": lesson_id}
            logger.info(
                f"Retrieving {k} chunks for query: '{query}' (lesson {lesson_id})"
            )
        else:
            logger.info(f"Retrieving {k} chunks for query: '{query}' (all lessons)")

        # Perform similarity search
        results = self._vector_store.similarity_search(
            query=query, k=k, filter=filter_dict
        )

        logger.info(f"Retrieved {len(results)} relevant chunks")
        return results

    def retrieve_with_scores(
        self, query: str, k: int = None, lesson_id: Optional[int] = None
    ) -> List[tuple[Document, float]]:
        """
        Retrieve relevant chunks with similarity scores

        Args:
            query: User's question or topic
            k: Number of chunks to retrieve
            lesson_id: Optional filter for specific lesson

        Returns:
            List of (Document, score) tuples
        """
        if self._vector_store is None:
            raise RuntimeError("Vector store not initialized")

        k = k or settings.retrieval_k
        filter_dict = {"lesson_id": lesson_id} if lesson_id else None

        results = self._vector_store.similarity_search_with_score(
            query=query, k=k, filter=filter_dict
        )

        logger.info(f"Retrieved {len(results)} chunks with scores")
        return results

    def delete_collection(self) -> None:
        """Delete the entire collection (use with caution)"""
        if self._vector_store is not None:
            logger.warning("Deleting vector store collection")
            self._vector_store.delete_collection()
            self._vector_store = None
            logger.info("Collection deleted")

    @property
    def is_initialized(self) -> bool:
        """Check if vector store is initialized"""
        return self._vector_store is not None
