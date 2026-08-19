# AI Decision Flow

This project contains a Next.js frontend and a FastAPI backend connected by Inngest.

## Prerequisites
- Node.js (v18+)
- Python (3.10+)

## How to Run

You will need to open **three separate terminal windows** to run the complete stack locally.

### 1. Start the Inngest Dev Server (Terminal 1)
The Inngest Dev Server handles event routing between your frontend and backend locally.
```bash
cd ai-decision-flow/frontend
npx inngest-cli@latest dev
```
*(The Inngest UI will be available at http://127.0.0.1:8288)*

### 2. Start the Backend (Terminal 2)
The backend is a FastAPI server that registers the Inngest function. We pass `INNGEST_DEV=1` so it knows to connect to the local Inngest server instead of the cloud.
```bash
cd ai-decision-flow/backend
source venv/bin/activate
INNGEST_DEV=1 uvicorn main:app --reload
```
*(The backend will run on http://127.0.0.1:8000)*

### 3. Start the Frontend (Terminal 3)
The Next.js application containing the React Flow UI.
```bash
cd ai-decision-flow/frontend
npm run dev
```
*(The frontend will run on http://localhost:3000)*

### 4. Open the App
Once all three are running, open your browser and navigate to **[http://localhost:3000](http://localhost:3000)**!
