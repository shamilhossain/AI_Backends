from enum import Enum
from pydantic import BaseModel, Field

class Category(str, Enum):
    BILLING = "BILLING"
    TECHNICAL = "TECHNICAL"
    SALES = "SALES"
    GENERAL = "GENERAL"

class Urgency(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class TicketAnalysisOutput(BaseModel):
    category: Category = Field(..., description="Category of the ticket")
    urgency: Urgency = Field(..., description="Urgency of the ticket")
    summary: str = Field(..., description="1-sentence summary of the ticket")
    action_required: bool = Field(..., description="Whether action is required")
