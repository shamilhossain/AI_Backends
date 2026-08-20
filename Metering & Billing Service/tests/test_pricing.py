import pytest
from app.services import calculate_ai_cost
from app.pricing import (
    PRICE_INPUT_TOKEN_MICRO_CENTS,
    PRICE_CACHED_INPUT_TOKEN_MICRO_CENTS,
    PRICE_OUTPUT_TOKEN_MICRO_CENTS,
    PRICE_REASONING_TOKEN_MICRO_CENTS
)

def test_calculate_ai_cost_zeros():
    # If no tokens are used, the cost must be strictly 0
    assert calculate_ai_cost(0, 0, 0, 0) == 0

def test_calculate_ai_cost_correct_math():
    # Test a complex calculation
    cost = calculate_ai_cost(100, 50, 200, 100)
    expected = (
        100 * PRICE_INPUT_TOKEN_MICRO_CENTS +
        50 * PRICE_CACHED_INPUT_TOKEN_MICRO_CENTS +
        200 * PRICE_OUTPUT_TOKEN_MICRO_CENTS +
        100 * PRICE_REASONING_TOKEN_MICRO_CENTS
    )
    assert cost == expected

def test_cached_inputs_are_cheaper():
    # Strict validation that cached tokens cost less than standard input tokens
    assert PRICE_CACHED_INPUT_TOKEN_MICRO_CENTS < PRICE_INPUT_TOKEN_MICRO_CENTS

def test_reasoning_tokens_billed_as_output():
    # Strict validation that reasoning tokens are billed exactly as output tokens
    assert PRICE_REASONING_TOKEN_MICRO_CENTS == PRICE_OUTPUT_TOKEN_MICRO_CENTS
