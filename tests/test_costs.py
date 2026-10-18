"""Maliyet ve model bilgisi testleri - API cagrisi yapmaz, internet gerektirmez."""

import pytest

from tools.costs import (
    estimate_cost,
    format_cost,
    known_models,
    model_info,
    on_free_tier,
    supports_temperature,
)


def test_known_models_contains_default():
    assert "gemini-3.8-flash" in known_models()


def test_estimate_cost_matches_price_table():
    # gemini-3.8-flash: 0.75 USD / 1M input, 3.75 USD / 1M output
    assert estimate_cost("gemini-3.8-flash", 1_000_000, 0) == pytest.approx(0.75)
    assert estimate_cost("gemini-3.8-flash", 0, 1_000_000) == pytest.approx(3.75)


def test_estimate_cost_combines_input_and_output():
    cost = estimate_cost("gemini-3.8-flash", 500_000, 500_000)
    assert cost == pytest.approx(0.375 + 1.875)


def test_zero_tokens_is_free():
    assert estimate_cost("gemini-3.8-flash", 0, 0) == 0.0


def test_unknown_model_returns_none_instead_of_wrong_number():
    assert estimate_cost("bilinmeyen-model", 1000, 1000) is None
    assert model_info("bilinmeyen-model") is None


def test_format_cost_is_explicit_about_unknown_price():
    assert "bilinmiyor" in format_cost(None)
    assert format_cost(0.000123) == "$0.000123"


def test_flash_lite_is_cheaper_than_flash():
    lite = estimate_cost("gemini-3.5-flash-lite", 1_000_000, 1_000_000)
    flash = estimate_cost("gemini-3.8-flash", 1_000_000, 1_000_000)
    assert lite < flash


class TestModelCapabilities:
    """Yanlis model bilgisi sessizce yanlis istek gondermeye yol acar."""

    def test_gemini_3_6_plus_ignores_temperature(self):
        # Docs: Gemini 4 ve 3.6+ ornekleme parametrelerini yok sayar.
        assert supports_temperature("gemini-3.8-flash") is False
        assert supports_temperature("gemini-3.6-flash") is False
        assert supports_temperature("gemini-4-argon") is False

    def test_flash_lite_still_accepts_temperature(self):
        assert supports_temperature("gemini-3.5-flash-lite") is True
        assert supports_temperature("gemini-3.1-flash-lite") is True

    def test_unknown_model_defaults_to_no_temperature(self):
        assert supports_temperature("bilinmeyen-model") is False

    def test_argon_is_not_on_free_tier(self):
        assert on_free_tier("gemini-4-argon") is False
        assert on_free_tier("gemini-3.8-flash") is True
