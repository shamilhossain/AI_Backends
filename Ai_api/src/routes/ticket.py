import os
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from pydantic import ValidationError
from src.llm.schema import TicketInput, TicketAnalysisOutput, TicketCategory, UrgencyLevel

router = APIRouter()

# Read the system prompt
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "triage-v1.md"
LOGS_DIR = BASE_DIR / "logs"

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
    
    # First LLM call
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": ticket.text}
    ]
    
    def call_llm(msgs):
        res = client.chat.completions.create(
            model=os.environ.get("LLM_MODEL", "gpt-3.5-turbo"),
            messages=msgs,
            temperature=0.2
        )
        return res.choices[0].message.content
        
    try:
        raw_text = call_llm(messages)
        # Parse & Validate
        return TicketAnalysisOutput.model_validate_json(raw_text)
    except (ValidationError, json.JSONDecodeError) as e:
        error_details = str(e)
        broken_output = raw_text
        
        # Repair Once
        messages.append({"role": "assistant", "content": broken_output})
        messages.append({
            "role": "user", 
            "content": f"Your previous answer was rejected for this reason: {error_details}. Return only corrected JSON matching the schema."
        })
        
        try:
            raw_text_2 = call_llm(messages)
            return TicketAnalysisOutput.model_validate_json(raw_text_2)
        except (ValidationError, json.JSONDecodeError) as e2:
            # Quarantine & 422
            quarantine_file = LOGS_DIR / "quarantine.jsonl"
            quarantine_data = {
                "ticket_text": ticket.text,
                "broken_output": raw_text_2,
                "error": str(e2)
            }
            with open(quarantine_file, "a") as qf:
                qf.write(json.dumps(quarantine_data) + "\n")
            
            raise HTTPException(status_code=422, detail="Unprocessable Entity: Invalid LLM response")
    except Exception as e:
        # Catch other exceptions like API connectivity issues
        raise HTTPException(status_code=500, detail=str(e))
