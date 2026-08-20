# Prices in micro-cents (1 cent = 10,000 micro-cents) to avoid float math errors
# Example pricing (e.g., $5/1M input, $15/1M output)
# $5 = 500 cents = 5,000,000 micro-cents per 1,000,000 tokens => 5 micro-cents per token

PRICE_INPUT_TOKEN_MICRO_CENTS = 5
PRICE_CACHED_INPUT_TOKEN_MICRO_CENTS = 2  # Cheaper for cached inputs
PRICE_OUTPUT_TOKEN_MICRO_CENTS = 15
PRICE_REASONING_TOKEN_MICRO_CENTS = 15  # Billed exactly as output tokens
