from .pricing import (
    PRICE_INPUT_TOKEN_MICRO_CENTS,
    PRICE_CACHED_INPUT_TOKEN_MICRO_CENTS,
    PRICE_OUTPUT_TOKEN_MICRO_CENTS,
    PRICE_REASONING_TOKEN_MICRO_CENTS
)

def calculate_ai_cost(input_tokens: int, cached_input_tokens: int, output_tokens: int, reasoning_tokens: int) -> int:
    """
    Calculates the exact total AI cost in micro-cents using the pricing constants.
    """
    return (
        input_tokens * PRICE_INPUT_TOKEN_MICRO_CENTS +
        cached_input_tokens * PRICE_CACHED_INPUT_TOKEN_MICRO_CENTS +
        output_tokens * PRICE_OUTPUT_TOKEN_MICRO_CENTS +
        reasoning_tokens * PRICE_REASONING_TOKEN_MICRO_CENTS
    )
