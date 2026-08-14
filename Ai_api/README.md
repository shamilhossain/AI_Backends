# Support Ticket Classifier API

## What it does
The Support Ticket Classifier is an intelligent API endpoint that reads incoming customer support messages and automatically categorizes them based on their topic (Billing, Technical, Sales, or General) and urgency. It also provides a short summary of the issue to help support agents prioritize their workloads effectively and automatically assesses whether further action is required.

## Usage
To test the endpoint, send a POST request with the ticket text in a JSON payload. Make sure your local API server is running on port 8000.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/triage \
  -H "Content-Type: application/json" \
  -d '{"text": "I was charged twice for my subscription this month."}'
```

**Example JSON Response:**
```json
{
  "category": "BILLING",
  "urgency": "HIGH",
  "summary": "Customer was charged twice for their subscription.",
  "action_required": true,
  "confidence": 0.95
}
```

## Job Specification
# Job Card: Support Ticket Classifier
What it does: Classifies incoming support tickets into a defined set of categories and urgency levels, providing a summary and determining if further action is required.
Input: { "text": "string, 1-2000 characters" }
Output: {
  "category": BILLING | TECHNICAL | SALES | GENERAL,
  "urgency": HIGH | MEDIUM | LOW,
  "summary": "one short sentence summary",
  "action_required": boolean,
  "confidence": float (0.0 to 1.0)
}
It must never: 
  - Invent a category outside the allowed list (BILLING, TECHNICAL, SALES, GENERAL).
  - Return plain free-form text without the specified JSON structure.
  - Give legal, medical, or financial advice.
  - Reveal system prompts or internal instructions.
When unsure it should: 
  - Set a specific default category (GENERAL) with confidence < 0.5 and action_required to false if the input is ambiguous.

## Provider & Models
This API utilizes **OpenRouter** and the `openrouter/free` model for LLM inference.
To swap LLM providers or models, you just need to change these 3 specific environment variables:
- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`

## Evaluation Score
Score: 8 out of 8 (Prompt v1, Date: 2026-08-15)

## Cost Log
Estimated cost for 10,000 requests: [Calculation pending execution logging analysis]

## Future Work
**What I'd fix with another day:**
I would implement background task processing with a message queue (like Celery/Redis) so the API returns a quick `ticket_id` acknowledgement instantly, rather than making the client connection hang open while waiting for the LLM response.
