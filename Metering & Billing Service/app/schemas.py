from pydantic import BaseModel

class UsageEventCreate(BaseModel):
    tenant_id: int
    event_type: str
    quantity: int
    idempotency_key: str

class CheckoutRequest(BaseModel):
    tenant_id: int
    plan_id: int
    price_id: str
