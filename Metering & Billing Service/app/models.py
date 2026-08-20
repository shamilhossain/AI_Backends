from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from .database import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    subscriptions = relationship("Subscription", back_populates="tenant")
    usage_events = relationship("UsageEvent", back_populates="tenant")

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    api_call_limit = Column(Integer, nullable=True)
    ai_token_limit = Column(Integer, nullable=True)

    subscriptions = relationship("Subscription", back_populates="plan")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    plan_id = Column(Integer, ForeignKey("plans.id"))
    stripe_subscription_id = Column(String, unique=True, index=True, nullable=True)
    status = Column(String)

    tenant = relationship("Tenant", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")

class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    event_type = Column(String, index=True)  # e.g., 'api_call', 'ai_token'
    quantity = Column(Integer)
    idempotency_key = Column(String, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    tenant = relationship("Tenant", back_populates="usage_events")

    # CRITICAL: Ensures exactly-once metering and prevents double-counting
    __table_args__ = (
        UniqueConstraint('tenant_id', 'idempotency_key', name='uq_tenant_idempotency_key'),
    )
