"""Ortam degiskenlerini tek yerden okur (.env -> Settings)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = ROOT / "logs"
KNOWLEDGE_DIR = ROOT / "knowledge"


@dataclass(frozen=True)
class Settings:
    api_key: str | None
    model: str
    temperature: float
    max_tokens: int

    @property
    def is_ready(self) -> bool:
        return bool(self.api_key)


def load_settings() -> Settings:
    """`.env` dosyasini yukler ve ayarlari dondurur."""
    load_dotenv(ROOT / ".env")
    return Settings(
        api_key=os.getenv("OPENAI_API_KEY") or None,
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1024")),
    )
