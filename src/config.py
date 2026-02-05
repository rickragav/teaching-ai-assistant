"""
Simplified configuration for English Teacher AI Assistant
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application configuration settings"""

    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    max_openai_tokens: int = int(os.getenv("MAX_OPENAI_TOKENS", "500"))

    # Azure OpenAI Settings
    use_azure_openai: bool = os.getenv("USE_AZURE_OPENAI", "false").lower() == "true"
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    azure_openai_api_version: str = os.getenv(
        "AZURE_OPENAI_API_VERSION", "2024-02-15-preview"
    )
    azure_openai_embedding_deployment: str = os.getenv(
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small"
    )

    # Course Settings
    course_name: str = os.getenv("COURSE_NAME", "english-grammar")

    # Paths
    project_root: Path = Path(__file__).parent.parent
    database_path: str = "database/progress.db"
    transcriptions_path: Path = project_root / "data" / "transcriptions"
    chroma_path: Path = project_root / "data" / "chroma_db"

    @property
    def course_path(self) -> Path:
        """Get the path to the current course"""
        return self.transcriptions_path / self.course_name

    # Application Settings
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    passing_score: float = 0.7  # 70% to pass quiz

    # LLM Settings
    model_name: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 500

    # RAG Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_k: int = 3  # Number of chunks to retrieve

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()
