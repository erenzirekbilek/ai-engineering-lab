"""Maliyet hesabi testleri - API cagrisi yapmaz, internet gerektirmez."""

import pytest

from tools.costs import estimate_cost, format_cost, known_models


def test_known_models_not_empty():
    assert "gpt-4o-mini" in known_models()


def test_estimate_cost_matches_price_table():
    # gpt-4o-mini: 0.15 USD / 1M input, 0.60 USD / 1M output
    cost = estimate_cost("gpt-4o-mini", input_tokens=1_000_000, output_tokens=0)
    assert cost == pytest.approx(0.15)

    cost = estimate_cost("gpt-4o-mini", input_tokens=0, output_tokens=1_000_000)
    assert cost == pytest.approx(0.60)


def test_estimate_cost_combines_input_and_output():
    cost = estimate_cost("gpt-4o-mini", input_tokens=500_000, output_tokens=500_000)
    assert cost == pytest.approx(0.075 + 0.30)


def test_zero_tokens_is_free():
    assert estimate_cost("gpt-4o-mini", 0, 0) == 0.0


def test_unknown_model_returns_none_instead_of_wrong_number():
    assert estimate_cost("bilinmeyen-model", 1000, 1000) is None


def test_format_cost_is_explicit_about_unknown_price():
    assert "bilinmiyor" in format_cost(None)
    assert format_cost(0.000123) == "$0.000123"
