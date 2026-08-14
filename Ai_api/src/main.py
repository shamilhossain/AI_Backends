from fastapi import FastAPI
from src.routes.ticket import router as ticket_router

app = FastAPI(title="Support Ticket Classifier API")

app.include_router(ticket_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Support Ticket Classifier API"}
