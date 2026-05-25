from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ASI_",
        extra="ignore",
    )

    project_name: str = "Mini Semantic Search"
    api_prefix: str = "/api"
    frontend_title: str = "Mini Semantic Search"
    chroma_path: Path = BASE_DIR / "data" / "chroma"
    collection_name: str = "knowledge_chunks"
    chunk_size_words: int = 180
    chunk_overlap_words: int = 40
    max_search_results: int = 8
    request_timeout_seconds: float = 30.0
    max_pdf_bytes: int = 12_000_000
    log_level: str = "INFO"
    log_path: Path = BASE_DIR / "logs" / "app.log"


@lru_cache
def get_settings() -> Settings:
    return Settings()
