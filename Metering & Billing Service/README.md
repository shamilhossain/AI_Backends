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

## Setup & Run Instructions

1. **Create and Activate Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Environment Variables:**
   Create a `.env` file from the provided `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Add your `STRIPE_TEST_KEY` and `STRIPE_WEBHOOK_SECRET` to the `.env` file.

4. **Run the Server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

5. **Run the Tests:**
   ```bash
   pytest
   ```

## Limitations
- **Local Database**: Currently uses a local SQLite database, which is unsuitable for high-concurrency production deployments. A production environment should use PostgreSQL or similar.
- **Subscription Model**: Assumes a single active subscription per tenant in the quota enforcement flow for simplicity.
- **Idempotency**: Idempotency relies on a single string `idempotency_key` mapped to a tenant, which works well in SQLite but may require more robust time-to-live (TTL) handling via Redis in a distributed system.
