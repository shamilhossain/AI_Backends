# Definition of Done Evidence

Please paste your terminal logs, API responses, or screenshots below to prove each requirement is met.

## 1. Exactly-once Metering (Idempotency Test)
> **Requirement**: Ensure identical `idempotency_key` payloads do not double-count usage.
> **Instructions**: Submit the same payload twice to `/api/generate`. Paste the 200 OK responses and show that the `event_id` is reused or a "Duplicated" message is returned.

[PASTE LOGS/SCREENSHOTS HERE]

## 2. Quota Boundary (429/402 Responses)
> **Requirement**: Reject usage events when limits are exceeded or no active plan exists.
> **Instructions**: Attempt to submit usage that pushes the tenant over their API/token limit. Paste the `429 Too Many Requests` or `402 Payment Required` HTTP response.

[PASTE LOGS/SCREENSHOTS HERE]

## 3. Monthly Cost Rollup and AI Token Pricing
> **Requirement**: Accurately calculate micro-cents cost based on distinct AI token pricing rules.
> **Instructions**: Call `GET /api/usage/{tenant_id}` and paste the JSON response showing `api_calls_used`, `ai_tokens_used`, and `total_cost_micro_cents`. Show the output of running `pytest`.

[PASTE LOGS/SCREENSHOTS HERE]

## 4. Stripe Webhooks (Success and Forged Rejection)
> **Requirement**: Correctly parse `checkout.session.completed` events and safely reject invalid signatures.
> **Instructions**: Send a real/test webhook and show the successful update. Send a forged webhook (or omit signature) and show the `400 Invalid signature` response.

[PASTE LOGS/SCREENSHOTS HERE]
