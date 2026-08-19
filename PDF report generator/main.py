import os
import sqlite3
from typing import Optional
from fastapi import FastAPI, HTTPException, status, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from report_generator import generate_pdf

app = FastAPI()

class ReportRequest(BaseModel):
    force: Optional[bool] = False

# Startup event to create the reports table
@app.on_event("startup")
def startup_event():
    conn = sqlite3.connect("report.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/reports", status_code=status.HTTP_201_CREATED)
async def create_report(response: Response, request: Optional[ReportRequest] = None):
    force = request.force if request else False
    
    conn = sqlite3.connect("report.db")
    cursor = conn.cursor()
    
    if not force:
        # Check if a report was already generated today
        # Both CURRENT_TIMESTAMP and 'now' use UTC, keeping this consistent
        cursor.execute("""
            SELECT id FROM reports 
            WHERE date(created_at) = date('now') 
            ORDER BY created_at DESC LIMIT 1
        """)
        existing_report = cursor.fetchone()
        
        if existing_report:
            conn.close()
            # Return 200 OK with the existing report details
            response.status_code = status.HTTP_200_OK
            report_id = existing_report[0]
            return {"id": report_id, "file": f"/reports/{report_id}/file"}
    
    # Insert a placeholder row to get the new auto-incremented ID
    cursor.execute("INSERT INTO reports (path) VALUES ('')")
    report_id = cursor.lastrowid
    
    # Define the PDF path based on the ID
    pdf_path = f"reports/{report_id}.pdf"
    
    # Update the row with the correct path
    cursor.execute("UPDATE reports SET path = ? WHERE id = ?", (pdf_path, report_id))
    conn.commit()
    conn.close()
    
    # Run the PDF generation pipeline asynchronously
    await generate_pdf(pdf_path)
    
    # Return 201 with the required payload
    return {"id": report_id, "file": f"/reports/{report_id}/file"}

@app.get("/reports/{report_id}")
def get_report(report_id: int):
    conn = sqlite3.connect("report.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, path, created_at FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Report not found")
        
    return {
        "id": row[0],
        "path": row[1],
        "created_at": row[2]
    }

@app.get("/reports/{report_id}/file")
def get_report_file(report_id: int):
    conn = sqlite3.connect("report.db")
    cursor = conn.cursor()
    cursor.execute("SELECT path FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Report not found")
        
    pdf_path = row[0]
    
    # Check if file actually exists on disk
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")
        
    # Serve the actual PDF file
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"report_{report_id}.pdf")
