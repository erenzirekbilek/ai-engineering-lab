"""Token kullanimindan tahmini maliyet hesaplar.

Fiyatlar `pricing.json` icinde ve UCRETLI kademeyi temsil eder. Ucretsiz
kademede ayni cagri $0'dir; buradaki rakam "ucretli kademeye gecersem ne
oderdim" sorusunun cevabidir.

Model listede yoksa maliyet None doner - yanlis bir rakam gostermektense
"bilinmiyor" demek daha dogru.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

PRICING_FILE = Path(__file__).resolve().parent / "pricing.json"


@lru_cache(maxsize=1)
def _models() -> dict[str, dict[str, Any]]:
    data = json.loads(PRICING_FILE.read_text(encoding="utf-8"))
    return data["models"]


def known_models() -> list[str]:
    return list(_models())


def model_info(model: str) -> dict[str, Any] | None:
    return _models().get(model)


def supports_temperature(model: str) -> bool:
    """Gemini 3.6+ ve 4 ailesi ornekleme parametrelerini yok sayar."""
    info = model_info(model)
    return bool(info and info.get("supports_temperature"))


def on_free_tier(model: str) -> bool:
    info = model_info(model)
    return bool(info and info.get("free_tier"))


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float | None:
    """Ucretli kademedeki tahmini USD maliyet. Model bilinmiyorsa None.

    `output_tokens`'a dusunme (thought) token'larini da dahil et: Gemini
    bunlari cikti tarafinda faturalandirir.
    """
    info = model_info(model)
    if info is None:
        return None
    return (input_tokens * info["input"] + output_tokens * info["output"]) / 1_000_000


def format_cost(cost: float | None) -> str:
    if cost is None:
        return "fiyat bilinmiyor (tools/pricing.json'a ekle)"
    return f"${cost:.6f}"
