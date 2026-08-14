from enum import Enum
from pydantic import BaseModel, Field

class TicketCategory(str, Enum):
    BILLING = "BILLING"
    TECHNICAL = "TECHNICAL"
    SALES = "SALES"
    GENERAL = "GENERAL"

class UrgencyLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class TicketInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)

class TicketAnalysisOutput(BaseModel):
    category: TicketCategory
    urgency: UrgencyLevel
    summary: str
    action_required: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
