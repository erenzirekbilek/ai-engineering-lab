"""Gemini Interactions API etrafinda ince bir sarmalayici.

Tek sorumlulugu: istegi gonder, gecikme + token + maliyeti olc, logla,
hatalari anlasilir bir mesaja cevir. Haftalik derslerin hepsi bunu kullanir.

Not: Gemini'nin yeni Interactions API'si sohbet gecmisini sunucuda tutabilir
(`previous_interaction_id`). 2. haftada bunu kullanacagiz.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx
from google import genai
from google.genai import errors

from .config import Settings, load_settings
from .costs import estimate_cost, supports_temperature
from .logging_utils import log_event


class LabError(RuntimeError):
    """Kullaniciya gosterilebilir, anlasilir hata."""


@dataclass(frozen=True)
class ChatResult:
    text: str
    model: str
    interaction_id: str | None
    input_tokens: int
    output_tokens: int
    thought_tokens: int
    total_tokens: int
    latency_ms: int
    cost_usd: float | None


def get_client(settings: Settings | None = None) -> genai.Client:
    settings = settings or load_settings()
    if not settings.is_ready:
        raise LabError(
            "GEMINI_API_KEY bulunamadi. `cp .env.example .env` yapip "
            "https://aistudio.google.com/apikey adresinden aldigin anahtari yaz."
        )
    return genai.Client(api_key=settings.api_key)


def chat(
    user_input: Any,
    *,
    settings: Settings | None = None,
    model: str | None = None,
    system_instruction: str | None = None,
    temperature: float | None = None,
    max_output_tokens: int | None = None,
    previous_interaction_id: str | None = None,
) -> ChatResult:
    """Tek bir istek gonderir ve olculmus sonucu dondurur."""
    settings = settings or load_settings()
    model = model or settings.model
    max_output_tokens = max_output_tokens or settings.max_output_tokens

    generation_config: dict[str, Any] = {"max_output_tokens": max_output_tokens}
    # 3.6+ ve 4 ailesi temperature'i yok sayip deprecation uyarisi dondurur.
    if supports_temperature(model):
        generation_config["temperature"] = (
            settings.temperature if temperature is None else temperature
        )

    body: dict[str, Any] = {
        "model": model,
        "input": user_input,
        "generation_config": generation_config,
    }
    if system_instruction:
        body["system_instruction"] = system_instruction
    if previous_interaction_id:
        body["previous_interaction_id"] = previous_interaction_id

    client = get_client(settings)
    started = time.perf_counter()

    try:
        interaction = client.interactions.create(**body)
    except errors.APIError as exc:
        raise _fail(model, exc)
    except httpx.HTTPError as exc:
        raise _fail_simple(
            "connection", model, "Google'a baglanilamadi. Ag baglantisini kontrol et.", exc
        )

    latency_ms = int((time.perf_counter() - started) * 1000)
    usage = getattr(interaction, "usage", None)
    input_tokens = getattr(usage, "total_input_tokens", 0) or 0
    output_tokens = getattr(usage, "total_output_tokens", 0) or 0
    thought_tokens = getattr(usage, "total_thought_tokens", 0) or 0
    total_tokens = getattr(usage, "total_tokens", 0) or (input_tokens + output_tokens)

    cost = estimate_cost(model, input_tokens, output_tokens + thought_tokens)

    log_event(
        "chat.ok",
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        thought_tokens=thought_tokens,
        total_tokens=total_tokens,
        latency_ms=latency_ms,
        cost_usd=cost,
    )

    return ChatResult(
        text=interaction.output_text or "",
        model=model,
        interaction_id=getattr(interaction, "id", None),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        thought_tokens=thought_tokens,
        total_tokens=total_tokens,
        latency_ms=latency_ms,
        cost_usd=cost,
    )


_MESSAGES = {
    400: "Istek gecersiz (model adi veya parametre hatali olabilir).",
    401: "API anahtari gecersiz. aistudio.google.com/apikey adresinden yenisini al.",
    403: "Bu anahtarin bu modele erisimi yok. Ucretsiz kademede olmayan bir model olabilir.",
    404: "Model bulunamadi. Model adini kontrol et.",
    429: "Hiz/kota siniri asildi. Ucretsiz kademede dakikalik ve gunluk limit var; biraz bekle.",
}


def _fail(model: str, exc: errors.APIError) -> LabError:
    code = getattr(exc, "code", None)
    message = _MESSAGES.get(code) if isinstance(code, int) else None
    if message is None:
        message = (
            f"Google {code} dondu."
            if isinstance(code, int) and code >= 500
            else f"Beklenmeyen API hatasi: {exc}"
        )
    return _fail_simple(f"api_{code}", model, message, exc)


def _fail_simple(kind: str, model: str, message: str, exc: Exception) -> LabError:
    log_event("chat.error", kind=kind, model=model, detail=str(exc)[:500])
    return LabError(message)
