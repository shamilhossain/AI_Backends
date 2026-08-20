from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from . import models, schemas
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
        # Immediately return success to prevent double-counting and support safe retries
        return {
            "status": "success",
            "message": "Duplicated/retried request. Event already recorded.",
            "event_id": existing_event.id
        }

    # 2. Quota Enforcement
    # Fetch the tenant's plan via their subscription
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

    # Determine the limit based on the event_type
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

    # Calculate total current usage for the tenant and event_type
    total_usage = db.query(func.sum(models.UsageEvent.quantity)).filter(
        models.UsageEvent.tenant_id == event.tenant_id,
        models.UsageEvent.event_type == event.event_type
    ).scalar() or 0

    # Honest Boundaries check
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
