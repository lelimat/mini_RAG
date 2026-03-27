"""Application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    bible_url: str = os.getenv("BIBLE_URL", "https://openbible.com/textfiles/kjv.txt")
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data"))
    parsed_bible_path: Path = Path(os.getenv("PARSED_BIBLE_PATH", "./data/kjv_verses.jsonl"))
    chroma_path: Path = Path(os.getenv("CHROMA_PATH", "./chroma_db"))
    collection_name: str = os.getenv("COLLECTION_NAME", "bible_kjv")
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    default_top_k: int = int(os.getenv("DEFAULT_TOP_K", "5"))
    llm_api_key: str | None = os.getenv("LLM_API_KEY") or None
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    llm_api_base: str = os.getenv("LLM_API_BASE", "https://api.openai.com/v1").rstrip("/")
    llm_timeout_seconds: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))

    def ensure_directories(self) -> None:
        """Create required local directories if they do not exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_path.mkdir(parents=True, exist_ok=True)


settings = Settings()
