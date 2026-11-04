from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    repo_dir: Path
    llm_base_url: str
    llm_api_key: str
    llm_model: str
    embedding_model: str
    embedding_backend: str
    seed: int
    validator: str
    cache_dir: Path
    artifacts_dir: Path


def get_settings() -> Settings:
    return Settings(
        repo_dir=ROOT / os.getenv("REPO_DIR", ".repos/fastapi"),
        llm_base_url=os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1"),
        llm_api_key=os.getenv("LLM_API_KEY", ""),
        llm_model=os.getenv("LLM_MODEL", "deepseek/deepseek-flash"),
        embedding_model=os.getenv(
            "EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2"
        ),
        embedding_backend=os.getenv("EMBEDDING_BACKEND", "auto"),
        seed=int(os.getenv("SEED", "42")),
        validator=os.getenv("VALIDATOR", "offline"),
        cache_dir=ROOT / ".cache",
        artifacts_dir=ROOT / "artifacts",
    )
