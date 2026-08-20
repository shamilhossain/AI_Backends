# flyrank-capstone-metering-billing

## Overview
This is a comprehensive Usage Metering & Billing Engine built with Python and FastAPI. It is designed to handle core features for SaaS platforms, including exactly-once metering, honest quota enforcement, Stripe payment integration, and exact AI token cost calculations.

## Architecture Diagram
```text
  +-------------+       +---------------+       +-----------------+
  |  API Client | ----> |  FastAPI App  | <---> | SQLite Database |
  +-------------+       +---------------+       +-----------------+
                               ^
                               | (Webhooks)
                               v
                       +---------------+
                       |    Stripe     |
                       +---------------+
```

## Features
- **Exactly-once Metering**: Uses unique `idempotency_key` constraints to ensure events are never double-counted, even if a request is retried by the client.
- **Quota Boundaries**: Enforces honest usage boundaries. If a user exceeds their AI token or API call limit as defined in their plan, the API strictly rejects the request with a `429 Too Many Requests`. If they lack a plan, it returns a `402 Payment Required`.
- **Granular AI Cost Calculation**: Prices are processed in micro-cents to prevent floating-point inaccuracies. Standard input, cached input, output, and reasoning tokens are distinctively tracked and priced.
- **Stripe Integration**: Generates Stripe checkout sessions for subscription upgrades and securely processes `checkout.session.completed` webhooks using signature verification.

## Project Structure
- `app/main.py`: The core FastAPI application containing all endpoints.
- `app/models.py`: SQLAlchemy database models (`Tenant`, `Plan`, `Subscription`, `UsageEvent`).
- `app/schemas.py`: Pydantic validation schemas for API inputs.
- `app/database.py`: SQLite engine and database session manager.
- `app/pricing.py`: AI token cost configurations stored in micro-cents.
- `app/services.py`: Business logic for computing AI token usage cost.
- `app/stripe_service.py`: Interfaces with the Stripe SDK to create checkouts.
- `tests/`: Contains strict Pytest unit tests for accurate billing calculation.

---

## Setup & Installation

1. **Clone the Repository** (If you haven't already):
   ```bash
   git clone <your-repo-url>
   cd "Metering & Billing Service"
   ```

2. **Create and Activate a Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Open the `.env` file and add your Stripe API keys:
   ```env
   STRIPE_TEST_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

## Running the Application

Start the local server using Uvicorn:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.
You can view the interactive API documentation (Swagger UI) by navigating to [http://localhost:8000/docs](http://localhost:8000/docs).

## Testing

To run the unit tests (which verify the micro-cent pricing math rules):
```bash
pytest
```
The tests guarantee that cached inputs are cheaper, reasoning tokens are billed exactly as output tokens, and calculations strictly equate correctly without float errors.

---

## API Usage & Endpoints

### 1. `POST /api/checkout`
Generates a Stripe checkout session URL to upgrade a tenant to a new plan.
**Payload:**
```json
{
  "tenant_id": 1,
  "plan_id": 2,
  "price_id": "price_1xxxxxxxxx"
}
```
**Response:** Returns a `checkout_url` to redirect the user to Stripe.

### 2. `POST /webhooks/stripe`
Listens for events from Stripe (e.g. `checkout.session.completed`). Validates the webhook signature from the raw body. Upon a successful event, it extracts the metadata and idempotently updates the database to activate the tenant's new subscription. 

### 3. `POST /api/generate`
Records a usage event (`api_call` or `ai_token`).
**Payload:**
```json
{
  "tenant_id": 1,
  "event_type": "ai_token",
  "quantity": 500,
  "idempotency_key": "req_abc123"
}
```
**Behavior:**
- **Idempotency**: If `req_abc123` already exists for this tenant, it returns a 200 OK immediately without double-counting.
- **Limits**: It aggregates previous usage. If 500 tokens put the tenant over their plan limit, it throws a `429 Too Many Requests`.
- **Save**: Otherwise, the event is securely recorded in the database.

### 4. `GET /api/usage/{tenant_id}`
Returns an aggregated report of the user's total usage and costs.
**Response Example:**
```json
{
  "tenant_id": 1,
  "plan_limits": {
    "api_call_limit": 1000,
    "ai_token_limit": 50000
  },
  "usage": {
    "api_calls_used": 15,
    "ai_tokens_used": 4200
  },
  "total_cost_micro_cents": 21000
}
```

---

## Limitations
- **Local Database**: Currently uses a local SQLite database, which is unsuitable for high-concurrency production deployments. A production environment should use PostgreSQL or similar.
- **Subscription Model**: Assumes a single active subscription per tenant in the quota enforcement flow for simplicity.
- **Idempotency**: Idempotency relies on a single string `idempotency_key` mapped to a tenant, which works well in SQLite but may require more robust time-to-live (TTL) handling via Redis in a distributed system.
