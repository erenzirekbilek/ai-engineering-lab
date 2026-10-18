"""OpenAI Chat Completions etrafinda ince bir sarmalayici.

Tek sorumlulugu: istegi gonder, gecikme + token + maliyeti olc, logla,
hatalari anlasilir bir mesaja cevir. Haftalik derslerin hepsi bunu kullanir.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    RateLimitError,
)

from .config import Settings, load_settings
from .costs import estimate_cost
from .logging_utils import log_event

Message = dict[str, str]


class LabError(RuntimeError):
    """Kullaniciya gosterilebilir, anlasilir hata."""


@dataclass(frozen=True)
class ChatResult:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cost_usd: float | None

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


def get_client(settings: Settings | None = None) -> OpenAI:
    settings = settings or load_settings()
    if not settings.is_ready:
        raise LabError(
            "OPENAI_API_KEY bulunamadi. `cp .env.example .env` yapip anahtarini yaz."
        )
    return OpenAI(api_key=settings.api_key)


def chat(
    messages: list[Message],
    *,
    settings: Settings | None = None,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> ChatResult:
    """Tek bir chat istegi gonderir ve olculmus sonucu dondurur."""
    settings = settings or load_settings()
    model = model or settings.model
    temperature = settings.temperature if temperature is None else temperature
    max_tokens = max_tokens or settings.max_tokens

    client = get_client(settings)
    started = time.perf_counter()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except AuthenticationError as exc:
        raise _fail("auth", model, "API anahtari gecersiz ya da suresi dolmus.", exc)
    except RateLimitError as exc:
        raise _fail("rate_limit", model, "Hiz/kota siniri asildi. Biraz bekleyip tekrar dene.", exc)
    except BadRequestError as exc:
        raise _fail("bad_request", model, f"Istek gecersiz (model adi veya parametre?): {exc}", exc)
    except APIConnectionError as exc:
        raise _fail("connection", model, "OpenAI'a baglanilamadi. Ag baglantisini kontrol et.", exc)
    except APIStatusError as exc:
        raise _fail("api_status", model, f"OpenAI {exc.status_code} dondu.", exc)

    latency_ms = int((time.perf_counter() - started) * 1000)
    usage = response.usage
    input_tokens = usage.prompt_tokens if usage else 0
    output_tokens = usage.completion_tokens if usage else 0
    cost = estimate_cost(model, input_tokens, output_tokens)

    log_event(
        "chat.ok",
        model=model,
        temperature=temperature,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        cost_usd=cost,
    )

    return ChatResult(
        text=response.choices[0].message.content or "",
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        cost_usd=cost,
    )


def _fail(kind: str, model: str, message: str, exc: Exception) -> LabError:
    log_event("chat.error", kind=kind, model=model, detail=str(exc)[:500])
    return LabError(message)
