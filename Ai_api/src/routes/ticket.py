import os
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from src.llm.schema import TicketInput, TicketAnalysisOutput, TicketCategory, UrgencyLevel

router = APIRouter()

# Read the system prompt
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "triage-v1.md"

with open(PROMPT_PATH, "r") as f:
    SYSTEM_PROMPT = f.read()

# Initialize OpenAI client
client = OpenAI(
    base_url=os.environ.get("LLM_BASE_URL"),
    api_key=os.environ.get("LLM_API_KEY", "dummy-api-key")
)

@router.post("/api/v1/triage", response_model=TicketAnalysisOutput)
async def triage_ticket(ticket: TicketInput):
    """
    Triage an incoming support ticket.
    """
    if os.environ.get("LLM_STUB") == "1":
        return TicketAnalysisOutput(
            category=TicketCategory.BILLING,
            urgency=UrgencyLevel.HIGH,
            summary="User is reporting a billing issue.",
            action_required=True,
            confidence=0.95
        )
    
    try:
        response = client.chat.completions.create(
            model=os.environ.get("LLM_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": ticket.text}
            ],
            temperature=0.2
        )
        
        response_text = response.choices[0].message.content
        parsed_response = json.loads(response_text)
        
        return parsed_response
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse LLM response as JSON.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
