"""
RAG Document Loader - Loads and chunks lesson transcriptions from JSON database
"""

from pathlib import Path
from typing import List, Dict
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from ..config import settings
from ..database.connection import db
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class LessonLoader:
    """Load and process lesson transcriptions from JSON database"""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        logger.info("LessonLoader initialized with JSON database backend")

    def load_lesson_from_content(
        self,
        content: str,
        course_id: str,
        section_id: str,
        lesson_id: str,
        lesson_title: str,
        section_title: str,
    ) -> List[Document]:
        """
        Load and chunk a lesson from text content

        Args:
            content: Lesson transcription text
            course_id: Course identifier
            section_id: Section identifier
            lesson_id: Lesson identifier
            lesson_title: Lesson title
            section_title: Section title

        Returns:
            List of Document objects with chunks and metadata
        """
        # Create document from content
        document = Document(
            page_content=content,
            metadata={
                "course_id": course_id,
                "section_id": section_id,
                "lesson_id": lesson_id,
                "lesson_title": lesson_title,
                "section_title": section_title,
                "source": "json_database",
            },
        )

        # Split into chunks
        chunks = self.text_splitter.split_documents([document])
        logger.info(f"Split lesson {lesson_id} into {len(chunks)} chunks")

        return chunks

    def load_all_lessons(self) -> List[Document]:
        """
        Load all available lessons from JSON database

        Returns:
            List of all Document chunks from all courses/sections/lessons
        """
        all_chunks = []
        courses = db.get_all_courses()

        if not courses:
            logger.warning("No courses found in database")
            return []

        logger.info(f"Found {len(courses)} courses in database")

        for course_id, course_data in courses.items():
            if course_data.get("status") != "published":
                logger.info(f"Skipping unpublished course: {course_id}")
                continue

            sections = course_data.get("sections", [])

            for section in sections:
                section_id = section.get("id", "")
                section_title = section.get("title", "")
                lessons = section.get("lessons", [])

                for lesson in lessons:
                    lesson_id = lesson.get("id", "")
                    lesson_title = lesson.get("title", "")
                    content = lesson.get("content", "")

                    if not content:
                        logger.warning(f"Empty content for lesson {lesson_id}")
                        continue

                    try:
                        chunks = self.load_lesson_from_content(
                            content,
                            course_id,
                            section_id,
                            lesson_id,
                            lesson_title,
                            section_title,
                        )
                        all_chunks.extend(chunks)
                    except Exception as e:
                        logger.error(f"Failed to load lesson {lesson_id}: {e}")
                        continue

        logger.info(f"Loaded total of {len(all_chunks)} chunks from database")
        return all_chunks

    def get_lesson_metadata(self) -> Dict[int, Dict]:
        """
        Get metadata about available lessons from JSON database

        Returns:
            Dict mapping sequential lesson_id to metadata
        """
        metadata = {}
        courses = db.get_all_courses()

        if not courses:
            logger.warning("No courses found in database")
            return metadata

        lesson_counter = 1
        for course_id, course_data in courses.items():
            if course_data.get("status") != "published":
                continue

            course_title = course_data.get("title", "")
            sections = course_data.get("sections", [])

            for section in sections:
                section_id = section.get("id", "")
                section_title = section.get("title", "")
                lessons = section.get("lessons", [])

                for lesson in lessons:
                    lesson_id = lesson.get("id", "")
                    lesson_title = lesson.get("title", "")
                    content = lesson.get("content", "")

                    metadata[lesson_counter] = {
                        "lesson_id": lesson_counter,
                        "db_lesson_id": lesson_id,
                        "course_id": course_id,
                        "course_title": course_title,
                        "section_id": section_id,
                        "section_title": section_title,
                        "title": lesson_title,
                        "content_length": len(content),
                    }
                    lesson_counter += 1

        logger.info(f"Retrieved metadata for {len(metadata)} lessons")
        return metadata
