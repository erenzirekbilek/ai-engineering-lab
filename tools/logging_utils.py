"""Her istegi logs/usage.jsonl dosyasina tek satir JSON olarak yazar.

6. haftadaki "loglama, gecikme ve token maliyeti olcumu" adimi bu dosyayi okur.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from .config import LOGS_DIR

USAGE_LOG = LOGS_DIR / "usage.jsonl"


def log_event(event: str, **fields: Any) -> None:
    """Log yazimi hicbir zaman uygulamayi dusurmemeli."""
    LOGS_DIR.mkdir(exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "event": event,
        **fields,
    }
    try:
        with USAGE_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def read_events(limit: int = 50) -> list[dict[str, Any]]:
    if not USAGE_LOG.exists():
        return []
    lines = USAGE_LOG.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:] if line.strip()]
