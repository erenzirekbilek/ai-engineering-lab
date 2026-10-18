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
    max_output_tokens: int

    @property
    def is_ready(self) -> bool:
        return bool(self.api_key)


def load_settings() -> Settings:
    """`.env` dosyasini yukler ve ayarlari dondurur.

    google-genai istemcisi anahtari GEMINI_API_KEY'den kendisi de okuyabilir,
    ama anahtarin var olup olmadigini arayuzde gosterebilmek icin burada da
    aciktan okuyoruz.
    """
    load_dotenv(ROOT / ".env")
    return Settings(
        api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or None,
        model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        temperature=float(os.getenv("GEMINI_TEMPERATURE", "1.0")),
        max_output_tokens=int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "1024")),
    )
