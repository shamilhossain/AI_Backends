from fastapi import APIRouter, status
from pydantic import BaseModel
from celery.result import AsyncResult

from src.worker import process_ticket_task, celery_app

router = APIRouter()

class TicketRequest(BaseModel):
    ticket_text: str

@router.post("/api/v1/triage", status_code=status.HTTP_202_ACCEPTED)
async def triage_ticket(request: TicketRequest):
    # Dispatch the job to Celery
    task = process_ticket_task.delay(request.ticket_text)
    
    return {
        "job_id": task.id,
        "message": "Ticket processing started in background"
    }

@router.get("/api/v1/status/{job_id}")
async def get_triage_status(job_id: str):
    # Check the Celery task status using our configured app instance
    task_result = AsyncResult(job_id, app=celery_app)
    
    response = {
        "job_id": job_id,
        "status": task_result.status,
    }
    
    if task_result.status == "SUCCESS":
        # The JSON dict returned by our worker
        response["result"] = task_result.result
    elif task_result.status == "FAILURE":
        response["error"] = str(task_result.result)
        
    return response
