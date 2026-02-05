"""
Simplified database connection for progress tracking using JSON
"""

import json
from pathlib import Path
from threading import Lock
from ..config import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class JSONDatabase:
    """Simple JSON file-based database manager"""

    def __init__(self, db_path: str = None):
        # Replace .db extension with .json
        if db_path:
            self.db_path = db_path.replace(".db", ".json")
        else:
            self.db_path = settings.database_path.replace(".db", ".json")

        self._lock = Lock()  # Thread-safe file operations
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Create JSON file if doesn't exist"""
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        if not db_file.exists():
            logger.info(f"Creating new JSON database at {self.db_path}")
            self._initialize_db()
        else:
            logger.info(f"Using existing JSON database at {self.db_path}")

    def _initialize_db(self):
        """Initialize empty database structure"""
        initial_data = {
            "users": {},  # user_id -> user_data mapping
            "courses": {}  # course_id -> course_data mapping
        }
        self._write_data(initial_data)
        logger.info("JSON database initialized successfully")

    def _read_data(self):
        """Read data from JSON file"""
        with self._lock:
            try:
                with open(self.db_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.error(f"Error reading database: {e}")
                return {"users": {}, "courses": {}}

    def _write_data(self, data):
        """Write data to JSON file"""
        with self._lock:
            try:
                with open(self.db_path, "w") as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                logger.error(f"Error writing database: {e}")
                raise

    def get_user(self, user_id: str):
        """Get user data"""
        data = self._read_data()
        return data["users"].get(user_id)

    def save_user(self, user_id: str, user_data: dict):
        """Save or update user data"""
        data = self._read_data()
        data["users"][user_id] = user_data
        self._write_data(data)

    # Course management methods
    def get_all_courses(self):
        """Get all courses"""
        data = self._read_data()
        return data.get("courses", {})

    def get_course(self, course_id: str):
        """Get specific course data"""
        data = self._read_data()
        return data.get("courses", {}).get(course_id)

    def save_course(self, course_id: str, course_data: dict):
        """Save or update course data"""
        data = self._read_data()
        if "courses" not in data:
            data["courses"] = {}
        data["courses"][course_id] = course_data
        self._write_data(data)

    def delete_course(self, course_id: str):
        """Delete a course"""
        data = self._read_data()
        if "courses" in data and course_id in data["courses"]:
            del data["courses"][course_id]
            self._write_data(data)
            return True
        return False


# Global database instance
db = JSONDatabase()
