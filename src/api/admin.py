"""
Admin API Routes for Course Management (Backoffice)
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import uuid
from pathlib import Path

from ..database.connection import db
from ..utils.logger import setup_logger
from ..rag.setup import setup_rag_system

logger = setup_logger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


# Serve Admin Dashboard (Main Page)
@router.get("/", response_class=HTMLResponse)
async def admin_dashboard():
    """Serve the main admin dashboard with navigation"""
    html_path = Path(__file__).parent.parent.parent / "admin-dashboard.html"
    
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="Admin dashboard not found")
    
    with open(html_path, "r") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)


# Serve Create Course Page
@router.get("/create", response_class=HTMLResponse)
async def create_course_page():
    """Serve the create course interface"""
    html_path = Path(__file__).parent.parent.parent / "admin-create-course.html"
    
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="Create course page not found")
    
    with open(html_path, "r") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)


# Serve Edit Course Page
@router.get("/edit", response_class=HTMLResponse)
async def edit_course_page():
    """Serve the edit course interface"""
    html_path = Path(__file__).parent.parent.parent / "admin-edit-course.html"
    
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="Edit course page not found")
    
    with open(html_path, "r") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)


# Request/Response Models
class LessonCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    subtitle: str = Field(default="", max_length=500)
    content: str = Field(..., min_length=10)  # Transcription text
    order: int = Field(default=0, ge=0)


class SectionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    order: int = Field(default=0, ge=0)
    lessons: List[LessonCreate] = Field(default_factory=list)


class CourseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    sections: List[SectionCreate] = Field(default_factory=list)


class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|published|archived)$")


class CourseResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    sections_count: int
    lessons_count: int
    created_at: str
    updated_at: str


class CourseDetailResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    sections: List[Dict]
    created_at: str
    updated_at: str


@router.post("/courses", response_model=CourseResponse)
async def create_course(course: CourseCreate):
    """Create a new course with sections and lessons"""
    try:
        course_id = f"course_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()

        # Process sections and lessons
        sections = []
        total_lessons = 0
        
        for section_data in course.sections:
            section_id = f"section_{uuid.uuid4().hex[:8]}"
            lessons = []
            
            for lesson_data in section_data.lessons:
                lesson_id = f"lesson_{uuid.uuid4().hex[:8]}"
                lessons.append({
                    "id": lesson_id,
                    "title": lesson_data.title,
                    "subtitle": lesson_data.subtitle,
                    "content": lesson_data.content,
                    "order": lesson_data.order,
                    "created_at": timestamp
                })
                total_lessons += 1
            
            sections.append({
                "id": section_id,
                "title": section_data.title,
                "order": section_data.order,
                "lessons": lessons,
                "created_at": timestamp
            })

        course_data = {
            "id": course_id,
            "title": course.title,
            "description": course.description,
            "status": "published",
            "sections": sections,
            "created_at": timestamp,
            "updated_at": timestamp
        }

        db.save_course(course_id, course_data)
        
        logger.info(f"Created course {course_id}: {course.title} with {len(sections)} sections, {total_lessons} lessons")

        return CourseResponse(
            id=course_id,
            title=course.title,
            description=course.description,
            status="published",
            sections_count=len(sections),
            lessons_count=total_lessons,
            created_at=timestamp,
            updated_at=timestamp
        )

    except Exception as e:
        logger.error(f"Failed to create course: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create course: {str(e)}")


@router.get("/courses", response_model=List[CourseResponse])
async def list_courses():
    """List all courses"""
    try:
        courses = db.get_all_courses()
        
        result = []
        for course_id, course_data in courses.items():
            sections = course_data.get("sections", [])
            lessons_count = sum(len(section.get("lessons", [])) for section in sections)
            
            result.append(CourseResponse(
                id=course_id,
                title=course_data.get("title", ""),
                description=course_data.get("description", ""),
                status=course_data.get("status", "published"),
                sections_count=len(sections),
                lessons_count=lessons_count,
                created_at=course_data.get("created_at", ""),
                updated_at=course_data.get("updated_at", "")
            ))
        
        logger.info(f"Listed {len(result)} courses")
        return result

    except Exception as e:
        logger.error(f"Failed to list courses: {e}")
        raise HTTPException(status_code=500, detail="Failed to list courses")


@router.get("/courses/{course_id}", response_model=CourseDetailResponse)
async def get_course(course_id: str):
    """Get course details"""
    try:
        course = db.get_course(course_id)
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return CourseDetailResponse(
            id=course["id"],
            title=course["title"],
            description=course.get("description", ""),
            status=course.get("status", "published"),
            sections=course.get("sections", []),
            created_at=course.get("created_at", ""),
            updated_at=course.get("updated_at", "")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get course {course_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get course")


@router.put("/courses/{course_id}", response_model=CourseResponse)
async def update_course(course_id: str, course_update: CourseUpdate):
    """Update course metadata"""
    try:
        course = db.get_course(course_id)
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Update fields
        if course_update.title:
            course["title"] = course_update.title
        if course_update.description is not None:
            course["description"] = course_update.description
        if course_update.status:
            course["status"] = course_update.status
        
        course["updated_at"] = datetime.now().isoformat()
        
        db.save_course(course_id, course)
        
        sections = course.get("sections", [])
        lessons_count = sum(len(section.get("lessons", [])) for section in sections)
        
        logger.info(f"Updated course {course_id}")
        
        return CourseResponse(
            id=course_id,
            title=course["title"],
            description=course.get("description", ""),
            status=course.get("status", "published"),
            sections_count=len(sections),
            lessons_count=lessons_count,
            created_at=course.get("created_at", ""),
            updated_at=course["updated_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update course {course_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update course")


@router.delete("/courses/{course_id}")
async def delete_course(course_id: str):
    """Delete a course"""
    try:
        success = db.delete_course(course_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Course not found")
        
        logger.info(f"Deleted course {course_id}")
        return {"message": "Course deleted successfully", "course_id": course_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete course {course_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete course")


@router.post("/courses/{course_id}/sections")
async def add_section(course_id: str, section: SectionCreate):
    """Add a section to an existing course"""
    try:
        course = db.get_course(course_id)
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        section_id = f"section_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        
        lessons = []
        for lesson_data in section.lessons:
            lesson_id = f"lesson_{uuid.uuid4().hex[:8]}"
            lessons.append({
                "id": lesson_id,
                "title": lesson_data.title,
                "subtitle": lesson_data.subtitle,
                "content": lesson_data.content,
                "order": lesson_data.order,
                "created_at": timestamp
            })
        
        new_section = {
            "id": section_id,
            "title": section.title,
            "order": section.order,
            "lessons": lessons,
            "created_at": timestamp
        }
        
        if "sections" not in course:
            course["sections"] = []
        
        course["sections"].append(new_section)
        course["updated_at"] = timestamp
        
        db.save_course(course_id, course)
        
        logger.info(f"Added section {section_id} to course {course_id}")
        
        return {
            "message": "Section added successfully",
            "section": new_section
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add section to course {course_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to add section")


@router.post("/courses/{course_id}/upload-transcription")
async def upload_transcription(
    course_id: str,
    section_title: str = Form(...),
    lesson_title: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload a transcription file for a lesson"""
    try:
        course = db.get_course(course_id)
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Read file content
        content = await file.read()
        transcription_text = content.decode("utf-8")
        
        timestamp = datetime.now().isoformat()
        lesson_id = f"lesson_{uuid.uuid4().hex[:8]}"
        
        # Find or create section
        sections = course.get("sections", [])
        target_section = None
        
        for section in sections:
            if section["title"] == section_title:
                target_section = section
                break
        
        if not target_section:
            # Create new section
            section_id = f"section_{uuid.uuid4().hex[:8]}"
            target_section = {
                "id": section_id,
                "title": section_title,
                "order": len(sections),
                "lessons": [],
                "created_at": timestamp
            }
            sections.append(target_section)
        
        # Add lesson to section
        new_lesson = {
            "id": lesson_id,
            "title": lesson_title,
            "subtitle": section_title,
            "content": transcription_text,
            "order": len(target_section["lessons"]),
            "created_at": timestamp
        }
        
        target_section["lessons"].append(new_lesson)
        course["sections"] = sections
        course["updated_at"] = timestamp
        
        db.save_course(course_id, course)
        
        logger.info(f"Uploaded transcription for course {course_id}, section {section_title}, lesson {lesson_title}")
        
        return {
            "message": "Transcription uploaded successfully",
            "lesson": new_lesson
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload transcription: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload transcription: {str(e)}")


@router.post("/rebuild-vector-db")
async def rebuild_vector_database():
    """Rebuild the vector database from scratch with all published courses"""
    try:
        logger.info("Starting vector database rebuild...")
        
        # Force rebuild the RAG system
        vector_store = setup_rag_system(force_rebuild=True)
        
        # Get stats
        courses = db.get_all_courses()
        published_courses = sum(1 for c in courses.values() if c.get("status") == "published")
        
        total_lessons = 0
        for course in courses.values():
            if course.get("status") == "published":
                for section in course.get("sections", []):
                    total_lessons += len(section.get("lessons", []))
        
        logger.info(f"Vector database rebuilt successfully: {published_courses} courses, {total_lessons} lessons")
        
        return {
            "message": "Vector database rebuilt successfully",
            "stats": {
                "published_courses": published_courses,
                "total_lessons": total_lessons,
                "status": "completed"
            }
        }

    except Exception as e:
        logger.error(f"Failed to rebuild vector database: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to rebuild vector database: {str(e)}")


@router.get("/vector-db-stats")
async def get_vector_database_stats():
    """Get vector database statistics"""
    try:
        from pathlib import Path
        from ..config import settings
        
        chroma_path = Path(settings.chroma_path)
        store_exists = chroma_path.exists() and any(chroma_path.iterdir())
        
        # Get course stats
        courses = db.get_all_courses()
        published_courses = sum(1 for c in courses.values() if c.get("status") == "published")
        
        total_chunks = 0
        total_lessons = 0
        
        for course in courses.values():
            if course.get("status") == "published":
                for section in course.get("sections", []):
                    lessons = section.get("lessons", [])
                    total_lessons += len(lessons)
                    # Estimate chunks (avg ~1500 chars per chunk with 1000 chunk size)
                    for lesson in lessons:
                        content_length = len(lesson.get("content", ""))
                        total_chunks += max(1, content_length // 1000)
        
        # Check if vector store is initialized
        status = "initialized" if store_exists else "not_initialized"
        
        return {
            "status": status,
            "exists": store_exists,
            "indexed_courses": published_courses,
            "indexed_lessons": total_lessons,
            "estimated_chunks": total_chunks,
            "storage_path": str(chroma_path),
            "embedding_model": "text-embedding-3-small"
        }

    except Exception as e:
        logger.error(f"Failed to get vector database stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get vector database stats: {str(e)}")
