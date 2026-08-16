# Smart Ticket Queue (AsyncTriage API) 🚀

Welcome to the **Smart Ticket Queue**! This project is an enterprise-grade, asynchronous web API designed to read customer support messages and automatically categorize them using AI, without ever keeping the user waiting.

## 💡 What it does (and How it works)

If you are a beginner, think of a traditional API as a digital waiter. In a normal system, you give the waiter a request, and they go to the kitchen to cook it while you (and everyone behind you) wait. If 100 people order at once, the system crashes!

**Our API solves this using an Asynchronous Background Job System:**
1. **The Waiter (FastAPI):** When a customer sends a message like *"I was charged twice!"*, our API receives it instantly, drops it on a task queue, and immediately gives the user a "Job ID" (Token number). 
2. **The Ticket Board (Redis):** Acts as our queue system to safely hold all incoming messages.
3. **The Chef (Celery Worker):** A background worker that picks up tickets from Redis, securely passes them to our Large Language Model (LLM) with a strict System Prompt, and handles any network failures with **Automatic Retries**.

The AI acts like an automated triage agent and extracts:
* **Category:** BILLING, TECHNICAL, SALES, or GENERAL
* **Urgency:** HIGH, MEDIUM, or LOW
* **Summary:** A quick one-sentence summary.
* **Action Required:** A true/false flag for human intervention.

---

## 🛠️ Tech Stack
* **Web Framework:** FastAPI
* **Background Worker:** Celery
* **Message Broker / Queue:** Redis
* **AI / LLM:** OpenAI / OpenRouter API
* **Data Validation:** Pydantic

---

## 🚀 How to Run the Project

### 1. Prerequisites
Make sure you have Python and Redis installed on your system.
For Mac users:
```bash
brew install redis
brew services start redis
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory and add your API key (and the STUB flag if testing):
```env
LLM_API_KEY=your_api_key_here
LLM_STUB=1
```

### 4. Start the Servers (Requires 2 Terminals)
You need to run the API and the Background Worker at the same time. Make sure you are in the project folder and your virtual environment is active!

**Terminal 1 (Start the Celery Worker):**
```bash
.venv/bin/celery -A src.worker.celery_app worker --loglevel=info
```

**Terminal 2 (Start the FastAPI Server):**
```bash
uvicorn src.main:app --reload
```

---

## 🧪 Testing the API

### Step 1: Submit a Ticket (POST)
Send a support message to the API. It will respond instantly with a `job_id`.
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/triage" \
-H "Content-Type: application/json" \
-d '{"ticket_text": "I was charged twice for my subscription this month!"}'
```

**Response:**
```json
{
  "job_id": "c1ceb5ae-fba6-4f84-9da3-16e9bbefe44d",
  "message": "Ticket processing started in background"
}
```

### Step 2: Check the Status (GET)
Use the `job_id` to check if the AI has finished processing the ticket.
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/status/c1ceb5ae-fba6-4f84-9da3-16e9bbefe44d"
```

**Response (When finished):**
```json
{
  "job_id": "c1ceb5ae-fba6-4f84-9da3-16e9bbefe44d",
  "status": "SUCCESS",
  "result": {
    "category": "BILLING",
    "urgency": "HIGH",
    "summary": "The customer was charged twice for their subscription.",
    "action_required": true
  }
}
```

---

## 📂 Project Files Breakdown
* **`.env`**: Stores sensitive secrets (like `LLM_API_KEY`).
* **`requirements.txt`**: Python dependencies.
* **`src/main.py`**: The FastAPI web server entry point.
* **`src/routes/ticket.py`**: The web endpoints for submitting and checking tickets.
* **`src/worker.py`**: The Celery background worker logic (AI connection).
* **`src/llm/schema.py`**: Pydantic models for structured AI output.
* **`prompts/triage-v1.md`**: The instruction manual (prompt) sent to the AI.

---

## 📚 More Details
For a deeper dive into this project, you can check out the full detailed guide here:
📄 **[Smart Ticket Queue Book](./Smart_Ticket_Queue_Book.pdf)**
