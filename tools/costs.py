"""Token kullanimindan tahmini maliyet hesaplar.

Fiyatlar `pricing.json` icinde; model listede yoksa maliyet None doner
(yanlis bir rakam gostermektense "bilinmiyor" demek daha dogru).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

PRICING_FILE = Path(__file__).resolve().parent / "pricing.json"


@lru_cache(maxsize=1)
def _pricing() -> dict[str, dict[str, float]]:
    data = json.loads(PRICING_FILE.read_text(encoding="utf-8"))
    return data["models"]


def known_models() -> list[str]:
    return sorted(_pricing())


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float | None:
    """Tahmini USD maliyet. Model fiyat tablosunda yoksa None."""
    rates = _pricing().get(model)
    if rates is None:
        return None
    return (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000


def format_cost(cost: float | None) -> str:
    if cost is None:
        return "fiyat bilinmiyor (tools/pricing.json'a ekle)"
    return f"${cost:.6f}"
