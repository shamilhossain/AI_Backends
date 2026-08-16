# Smart Ticket Queue (AsyncTriage API) 🎫🤖

Welcome to the **Smart Ticket Queue** project! This is a beginner-friendly guide to understand what this project is, how it works, and why we built it.

---

## 🌟 What is it?
The Smart Ticket Queue is a backend web application built with **Python**. Its main job is to take customer support tickets (like complaints or questions) and use Artificial Intelligence (an LLM like OpenAI) to automatically analyze them. It figures out the category, how urgent it is, and summarizes the problem. 

## 🎯 Purpose (Why did we build this?)
When a company gets hundreds of customer support tickets, human agents have to read every single one to figure out who should handle it. 
We built this project to **automate the triage process**. Instead of a human reading it, the AI reads it instantly and categorizes it. 

We built it using a **background queue system**. AI requests can take several seconds to process. If we made the user wait on the screen for the AI to finish, the app would feel slow or freeze. Instead, we put the ticket in a background "queue" and instantly tell the user, *"We got it, check back in a few seconds!"*

## 💡 Where to use this?
This backend system can be used by:
- **Customer Support Dashboards:** To automatically sort incoming emails or chat messages.
- **Helpdesks:** To assign high-urgency tickets (like billing issues or server crashes) to the right team immediately.
- **Feedback Systems:** To analyze large amounts of customer feedback and categorize them.

---

## ⚙️ How does it work?

We use a modern stack of technologies to make this happen:
* **FastAPI:** The web server that handles HTTP requests (like sending and receiving data).
* **Redis:** The database/broker that holds our background jobs in a waiting line.
* **Celery:** The background worker that picks up jobs from Redis and does the heavy lifting (calling the AI).

### The Step-by-Step Flow:
1. **Submit:** You send a ticket text to the `/api/v1/triage` endpoint.
2. **Queue:** The FastAPI server instantly saves the ticket in Redis and gives you a `job_id`. It doesn't wait for the AI!
3. **Background Work:** The Celery worker sees the new job in Redis, takes the text, and sends it to the AI (OpenAI) with instructions.
4. **Result:** The AI returns the categorized data, and the Celery worker saves it back to Redis as `SUCCESS`.
5. **Check Status:** You use the `/api/v1/status/{job_id}` endpoint. If the job is done, it hands you the final structured data!

---

## 📂 Project Files (What they do and why we made them)

Here is a breakdown of every file we created and why it exists:

### 1. Configuration & Setup
* **`.env`**: This is a hidden file where we store sensitive secrets (like `LLM_API_KEY`). We never upload this to GitHub. It also holds our `LLM_STUB=1` setting, which lets us test the app with fake data so we don't have to pay for real AI API calls while coding!
* **`.gitignore`**: Tells Git which files to ignore (like the `.env` file and the massive `.venv` folder) so we don't upload junk to GitHub.
* **`requirements.txt`**: A simple text list of all the Python packages (like `fastapi`, `celery`, `redis`, `openai`) needed to run this project. Anyone downloading this project can type `pip install -r requirements.txt` to get everything they need.

### 2. The Core Application (`src/` folder)
* **`src/main.py`**: The main entry point of our web server. It starts FastAPI and connects our "routes" (endpoints) to the server so it can listen for web traffic.
* **`src/routes/ticket.py`**: This file contains the actual web addresses (endpoints) that users interact with. It has the `POST` route for submitting a ticket and the `GET` route for checking a ticket's status.
* **`src/worker.py`**: The heart of our background processing. This file contains the Celery code that connects to Redis, picks up tickets, calls the AI API, and handles errors (like retrying if the API crashes).
* **`src/llm/schema.py`**: We use a tool called Pydantic here. This file defines the exact "shape" or "blueprint" of the data we want the AI to return (Category, Urgency, Summary). It forces the AI to reply in a perfect, predictable format instead of random text.

### 3. AI Instructions
* **`prompts/triage-v1.md`**: This is the instruction manual we send to the AI. It tells the AI: *"You are an expert customer support agent. Read this ticket and extract the urgency and category..."* Keeping this in a separate file makes it easy to tweak the AI's behavior later without touching the Python code.

---

## 🚀 How to Test it Yourself

### 1. Start the Servers
Before you can test the API, you need to have two terminal windows open running our servers. Make sure you are in the project folder!

**Terminal 1 (Start FastAPI):**
```bash
uvicorn src.main:app --reload
```

**Terminal 2 (Start Celery Worker):**
```bash
.venv/bin/celery -A src.worker.celery_app worker --loglevel=info
```

### 2. Test the API
Open a third terminal window and run this command to submit a ticket:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/triage" -H "Content-Type: application/json" -d '{"ticket_text": "I was charged twice for my plan!"}'
```
You will get a response with a `job_id`. Copy that ID and run this command to see the AI's result:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/status/YOUR_JOB_ID_HERE"
```

---

## 📚 More Details
For a deeper dive into this project, you can check out the full detailed guide here:
📄 **[Smart Ticket Queue Book](./Smart_Ticket_Queue_Book.pdf)**
