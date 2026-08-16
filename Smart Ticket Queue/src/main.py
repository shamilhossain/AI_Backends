from fastapi import FastAPI
from src.routes.ticket import router as ticket_router

app = FastAPI(
    title="AsyncTriage API",
    description="Enterprise-grade background job system using FastAPI and Celery.",
    version="1.0.0"
)

# Include the ticket routes
app.include_router(ticket_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the AsyncTriage API!"}

