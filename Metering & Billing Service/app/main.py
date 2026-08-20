import os
import stripe
from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from . import models, schemas, stripe_service, services
from .database import engine, get_db

# Ensure all database tables are created on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Usage Metering & Billing Engine")

@app.post("/api/generate", status_code=status.HTTP_201_CREATED)
def generate_event(event: schemas.UsageEventCreate, db: Session = Depends(get_db)):
    # 1. Idempotency Check
    existing_event = db.query(models.UsageEvent).filter(
        models.UsageEvent.tenant_id == event.tenant_id,
        models.UsageEvent.idempotency_key == event.idempotency_key
    ).first()
    
    if existing_event:
        return {
            "status": "success",
            "message": "Duplicated/retried request. Event already recorded.",
            "event_id": existing_event.id
        }

    # 2. Quota Enforcement
    plan = db.query(models.Plan).join(models.Subscription).filter(
        models.Subscription.tenant_id == event.tenant_id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "Payment Required",
                "message": f"Tenant {event.tenant_id} does not have a subscription plan."
            }
        )

    limit = None
    if event.event_type == "api_call":
        limit = plan.api_call_limit
    elif event.event_type == "ai_token":
        limit = plan.ai_token_limit
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid Input", 
                "message": f"Unknown event type: {event.event_type}"
            }
        )

    total_usage = db.query(func.sum(models.UsageEvent.quantity)).filter(
        models.UsageEvent.tenant_id == event.tenant_id,
        models.UsageEvent.event_type == event.event_type
    ).scalar() or 0

    if limit is not None and (total_usage + event.quantity > limit):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Quota Exceeded",
                "message": f"Cannot process {event.quantity} units. Current usage is {total_usage} out of a limit of {limit} for {event.event_type}."
            }
        )

    # 3. Save Event
    new_event = models.UsageEvent(
        tenant_id=event.tenant_id,
        event_type=event.event_type,
        quantity=event.quantity,
        idempotency_key=event.idempotency_key
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return {
        "status": "success",
        "message": "Event successfully recorded.",
        "event_id": new_event.id
    }


@app.post("/api/checkout")
def create_checkout(request: schemas.CheckoutRequest):
    try:
        session = stripe_service.create_checkout_session(
            tenant_id=request.tenant_id,
            plan_id=request.plan_id,
            price_id=request.price_id
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if not endpoint_secret:
        raise HTTPException(status_code=500, detail="Stripe webhook secret not configured")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Extract metadata
        metadata = session.get("metadata", {})
        tenant_id_str = metadata.get("tenant_id")
        plan_id_str = metadata.get("plan_id")
        stripe_subscription_id = session.get("subscription")

        if not tenant_id_str or not plan_id_str:
            return {"status": "ignored", "message": "Missing metadata"}

        tenant_id = int(tenant_id_str)
        plan_id = int(plan_id_str)

        # Idempotency / Update Logic
        subscription = db.query(models.Subscription).filter(
            models.Subscription.tenant_id == tenant_id
        ).first()

        if subscription:
            if subscription.stripe_subscription_id == stripe_subscription_id and subscription.plan_id == plan_id:
                # Already processed this exact upgrade
                return {"status": "success", "message": "Already processed"}
            
            # Update existing subscription
            subscription.plan_id = plan_id
            subscription.stripe_subscription_id = stripe_subscription_id
            subscription.status = "active"
        else:
            # Create a new subscription if one doesn't exist
            new_subscription = models.Subscription(
                tenant_id=tenant_id,
                plan_id=plan_id,
                stripe_subscription_id=stripe_subscription_id,
                status="active"
            )
            db.add(new_subscription)
            
        db.commit()

    return {"status": "success"}


@app.get("/api/usage/{tenant_id}")
def get_usage(tenant_id: int, db: Session = Depends(get_db)):
    # 1. Fetch the tenant's plan via their active subscription
    plan = db.query(models.Plan).join(models.Subscription).filter(
        models.Subscription.tenant_id == tenant_id
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Tenant plan not found")

    # 2. Aggregate all API calls
    api_calls_used = db.query(func.sum(models.UsageEvent.quantity)).filter(
        models.UsageEvent.tenant_id == tenant_id,
        models.UsageEvent.event_type == "api_call"
    ).scalar() or 0

    # 3. Aggregate all AI tokens
    ai_tokens_used = db.query(func.sum(models.UsageEvent.quantity)).filter(
        models.UsageEvent.tenant_id == tenant_id,
        models.UsageEvent.event_type == "ai_token"
    ).scalar() or 0

    # 4. Calculate Total Cost using the calculate_ai_cost function
    # Assuming the currently logged tokens are all standard input for this endpoint demo
    total_cost_micro_cents = services.calculate_ai_cost(
        input_tokens=ai_tokens_used,
        cached_input_tokens=0,
        output_tokens=0,
        reasoning_tokens=0
    )

    # Return total usage, plan limits, and total calculated cost
    return {
        "tenant_id": tenant_id,
        "plan_limits": {
            "api_call_limit": plan.api_call_limit,
            "ai_token_limit": plan.ai_token_limit
        },
        "usage": {
            "api_calls_used": api_calls_used,
            "ai_tokens_used": ai_tokens_used
        },
        "total_cost_micro_cents": total_cost_micro_cents
    }
