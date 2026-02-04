"""
RAG Document Loader - Loads and chunks lesson transcriptions
"""

from pathlib import Path
from typing import List, Dict
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from ..config import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class LessonLoader:
    """Load and process lesson transcription files with course/section/lesson structure"""

    def __init__(self):
        self.course_path = settings.course_path
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        logger.info(f"Using course: {settings.course_name} at {self.course_path}")

    def load_lesson(
        self, section: str, lesson_name: str, lesson_id: int = None
    ) -> List[Document]:
        """
        Load and chunk a specific lesson from course/section/lesson structure

        Args:
            section: Section folder name (e.g., 'section1', 'section2')
            lesson_name: Lesson file name (e.g., 'lesson_1.txt')
            lesson_id: Optional lesson ID for metadata

        Returns:
            List of Document objects with chunks and metadata
        """
        lesson_file = self.course_path / section / lesson_name

        if not lesson_file.exists():
            logger.error(f"Lesson file not found: {lesson_file}")
            raise FileNotFoundError(f"Lesson not found at {lesson_file}")

        logger.info(f"Loading lesson from {lesson_file}")

        # Load the file
        loader = TextLoader(str(lesson_file), encoding="utf-8")
        documents = loader.load()

        # Add metadata
        for doc in documents:
            doc.metadata["course"] = settings.course_name
            doc.metadata["section"] = section
            doc.metadata["lesson_name"] = lesson_name
            if lesson_id:
                doc.metadata["lesson_id"] = lesson_id
            doc.metadata["source"] = str(lesson_file)

        # Split into chunks
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Split lesson into {len(chunks)} chunks")

        return chunks

    def load_all_lessons(self) -> List[Document]:
        """
        Load all available lesson transcriptions from course/section/lesson structure

        Returns:
            List of all Document chunks from all lessons
        """
        all_chunks = []

        if not self.course_path.exists():
            logger.error(f"Course path not found: {self.course_path}")
            return []

        # Find all section directories
        sections = sorted([d for d in self.course_path.iterdir() if d.is_dir()])

        if not sections:
            logger.warning(f"No sections found in {self.course_path}")
            return []

        logger.info(f"Found {len(sections)} sections in course: {settings.course_name}")

        lesson_counter = 1
        for section in sections:
            section_name = section.name
            logger.info(f"Loading section: {section_name}")

            # Find all lesson files in this section
            lesson_files = sorted(section.glob("*.txt"))

            for lesson_file in lesson_files:
                try:
                    chunks = self.load_lesson(
                        section_name, lesson_file.name, lesson_counter
                    )
                    all_chunks.extend(chunks)
                    lesson_counter += 1
                except Exception as e:
                    logger.error(f"Failed to load {lesson_file}: {e}")
                    continue

        logger.info(
            f"Loaded total of {len(all_chunks)} chunks from {lesson_counter - 1} lessons"
        )
        return all_chunks

    def get_lesson_metadata(self) -> Dict[int, Dict]:
        """
        Get metadata about available lessons from course/section/lesson structure

        Returns:
            Dict mapping lesson_id to metadata (title, section, file_path, etc.)
        """
        metadata = {}

        if not self.course_path.exists():
            logger.warning(f"Course path not found: {self.course_path}")
            return metadata

        sections = sorted([d for d in self.course_path.iterdir() if d.is_dir()])

        lesson_counter = 1
        for section in sections:
            section_name = section.name
            lesson_files = sorted(section.glob("*.txt"))

            for lesson_file in lesson_files:
                try:
                    with open(lesson_file, "r", encoding="utf-8") as f:
                        first_line = f.readline().strip()
                        title = (
                            first_line.replace("Lesson:", "").replace("#", "").strip()
                        )

                    metadata[lesson_counter] = {
                        "lesson_id": lesson_counter,
                        "course": settings.course_name,
                        "section": section_name,
                        "lesson_name": lesson_file.name,
                        "title": title,
                        "file_path": str(lesson_file),
                        "file_size": lesson_file.stat().st_size,
                    }
                    lesson_counter += 1
                except Exception as e:
                    logger.error(f"Failed to read metadata for {lesson_file}: {e}")
                    continue

        return metadata
