import os
import json
import time
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

# Initialize OpenAI client with explicit timeout and max_retries
client = OpenAI(
    base_url=os.environ.get("LLM_BASE_URL"),
    api_key=os.environ.get("LLM_API_KEY", "dummy-api-key"),
    timeout=30.0,
    max_retries=2
)

@router.post("/api/v1/triage", response_model=TicketAnalysisOutput)
async def triage_ticket(ticket: TicketInput):
    """
    Triage an incoming support ticket.
    """
    # Kill Switch
    if os.environ.get("LLM_ENABLED") == "false":
        return TicketAnalysisOutput(
            category=TicketCategory.GENERAL,
            urgency=UrgencyLevel.LOW,
            summary="Fallback mode active",
            action_required=False,
            confidence=0.0
        )

    # Stub Mode
    if os.environ.get("LLM_STUB") == "1":
        return TicketAnalysisOutput(
            category=TicketCategory.BILLING,
            urgency=UrgencyLevel.HIGH,
            summary="User is reporting a billing issue.",
            action_required=True,
            confidence=0.95
        )
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": ticket.text}
    ]
    
    total_prompt_tokens = 0
    total_completion_tokens = 0
    repair_count = 0
    model_name = os.environ.get("LLM_MODEL", "gpt-3.5-turbo")
    
    def call_llm(msgs):
        nonlocal total_prompt_tokens, total_completion_tokens
        res = client.chat.completions.create(
            model=model_name,
            messages=msgs,
            temperature=0.2
        )
        if res.usage:
            total_prompt_tokens += res.usage.prompt_tokens
            total_completion_tokens += res.usage.completion_tokens
        return res.choices[0].message.content
        
    start_time = time.time()
    
    try:
        raw_text = call_llm(messages)
        result = TicketAnalysisOutput.model_validate_json(raw_text)
    except (ValidationError, json.JSONDecodeError) as e:
        error_details = str(e)
        broken_output = raw_text
        repair_count += 1
        
        # Repair Once
        messages.append({"role": "assistant", "content": broken_output})
        messages.append({
            "role": "user", 
            "content": f"Your previous answer was rejected for this reason: {error_details}. Return only corrected JSON matching the schema."
        })
        
        try:
            raw_text_2 = call_llm(messages)
            result = TicketAnalysisOutput.model_validate_json(raw_text_2)
        except (ValidationError, json.JSONDecodeError) as e2:
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log cost before quarantining
            log_entry = {
                "event": "llm_cost_log",
                "model": model_name,
                "prompt_tokens": total_prompt_tokens,
                "completion_tokens": total_completion_tokens,
                "duration_ms": duration_ms,
                "repair_count": repair_count
            }
            print(json.dumps(log_entry))
            
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
        raise HTTPException(status_code=500, detail=str(e))
        
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Cost Logging on success
    log_entry = {
        "event": "llm_cost_log",
        "model": model_name,
        "prompt_tokens": total_prompt_tokens,
        "completion_tokens": total_completion_tokens,
        "duration_ms": duration_ms,
        "repair_count": repair_count
    }
    print(json.dumps(log_entry))
    
    return result
