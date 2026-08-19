# PDF Report Generator

This project is a FastAPI-based backend application that generates beautifully formatted PDF reports from database records. We chose **Option A: The little shop** as our dataset.

## How to Run the Application

1. **Install Dependencies:**
   Ensure you have the required dependencies installed (ideally in a virtual environment):
   ```bash
   pip install fastapi uvicorn playwright
   playwright install chromium
   ```

2. **Seed the Database:**
   Run the seed script to generate 200 random shop orders and load them into the SQLite database (`report.db`). It automatically clears any old data to prevent duplication.
   ```bash
   python seed.py
   ```

3. **Start the API Server:**
   Launch the FastAPI application with live reloading:
   ```bash
   uvicorn main:app --reload
   ```

## Raw SQL Aggregations

Here are the raw SQL queries we used to calculate the summary metrics for our PDF reports:

**Top 5 Products by Revenue:**
```sql
SELECT product, SUM(amount) as revenue
FROM orders
GROUP BY product
ORDER BY revenue DESC
LIMIT 5
```

**Orders per day for the last 7 days:**
```sql
SELECT date(created_at) as order_date, COUNT(*) as daily_orders
FROM orders
WHERE date(created_at) >= date('now', 'localtime', '-7 days')
GROUP BY order_date
ORDER BY order_date ASC
```

## Proof of Pipeline

You can generate a report by making a `POST` request to our API:

```bash
curl -X POST http://127.0.0.1:8000/reports
```

**Expected Response:**
```json
{"id": 1, "file": "/reports/1/file"}
```

You can then view or download the generated PDF by navigating to the download link in your browser:
[http://127.0.0.1:8000/reports/1/file](http://127.0.0.1:8000/reports/1/file)

## Technical Q&A

**At what point would you move this work out of the request?**
When the request takes too long (e.g., for heavy, complex reports), we risk keeping the user hostage and waiting for a response, or timing out the API request. At that point, we would move this work out of the synchronous request cycle and use background jobs (e.g., using Celery or Redis queues) to generate the report asynchronously.

**What does the idempotency check protect against, and a real-world example?**
The idempotency check protects against wasted server resources and duplicate file generation if a user double-clicks the "Generate" button or re-submits the exact same request. 
*Real-world example:* A user clicks "Send Monthly Report Email" twice by accident due to lag. An idempotency check ensures we never send that report email to a customer twice, protecting against spam and redundant database reads/PDF generations.

---

## Comprehensive Guide: Automated PDF Report Generation

Here is the complete, finalized documentation book, updated with the exact, highly detailed prompts you used to build the project. 

### Chapter 1: Introduction

**What is this?**
This is a complete backend software pipeline built using Python, FastAPI, SQLite, and Playwright. It is designed to take raw data from a database, calculate meaningful summaries, format those numbers into a clean web page, and seamlessly "print" that page into a downloadable PDF file.

**Why do we need this?**
Sending raw database rows to a client or a business manager is useless; they need insights, not data dumps. Furthermore, generating massive files and sending them directly through web requests slows down servers and creates a poor user experience. We need a system that processes data efficiently and safely serves the resulting files.

**The Core Purpose**
The core purpose of this project is to master two critical backend engineering concepts:
- **The "Store and Link" Pattern**: Instead of passing heavy 20MB files through API responses, the server saves the generated PDF to the hard drive and gives the user a lightweight, clickable download link.
- **Idempotency**: A fancy word for "safe to double-click." If a user impatiently clicks the "Generate" button multiple times, the server recognizes the duplicate request and returns the existing file instead of wasting CPU power generating the exact same PDF twice.

### Chapter 2: Real-Life Applications
This exact architecture is not just an assignment; it is a fundamental feature running inside almost every major SaaS (Software as a Service) platform today.

**Where is this used?**
- **E-Commerce**: Generating monthly sales summaries or customer receipts.
- **Fintech & Banking**: Creating monthly bank statements or tax export documents.
- **Healthcare**: Generating patient history records or lab result reports.

**How does it scale?**
In a massive real-world application, this process is usually moved to a **Background Job** (using tools like Celery or Inngest). Because generating a 100-page PDF might take 10 seconds, you don't want the user staring at a frozen browser tab. The API immediately says, "We are working on it!" and sends the download link to their email once the background job finishes. The files are also saved to cloud storage (like AWS S3) instead of a local computer folder.

### Chapter 3: Stage-by-Stage Implementation Guide
Here is the exact breakdown of how this system was built, including the exact instructions (Prompts) used to generate the code with 100% accuracy via an AI Agent.

**Stage 0 & 1: The Setup and Data Seeding**
Before we can report on data, we need a server and the data itself. We set up a basic FastAPI server to handle requests. Then, we wrote a Python script to create an SQLite database (`report.db`) and fill it with 200 fake shop orders. To make it safe to run multiple times, the script deletes any old data before inserting new data.

> **Exact AI Prompt Used**: "Act as an expert Python backend engineer. We are building a PDF report generator assignment. Create a basic web server using FastAPI in a file named `main.py` with a `GET /health` endpoint. Write a separate Python script named `seed.py` using sqlite3. The script must execute a `DELETE FROM orders` command to clear any old data before inserting new rows, then generate and insert exactly 200 random shop orders."

**Stage 2: Boring SQL is 80% of Reporting**
Nobody reads 200 lines of data. We used SQL (Structured Query Language) to aggregate the raw data into four key metrics: Total Orders, Total Revenue, Top 5 Products, and Recent Daily Sales.

> **Exact AI Prompt Used**: "Act as an expert Python backend engineer. Write a new Python file named `report_data.py`. Execute SQL queries to calculate and return a single dictionary containing 4 metrics: total_orders (COUNT), total_revenue (SUM), top_products (GROUP BY limit 5), and recent_sales (orders per day last 7 days). Print the resulting dictionary as formatted JSON."

**Stage 3: Render - From Numbers to PDF**
We took the calculated metrics and injected them into an HTML string. Then, we used Playwright (a headless browser automation tool) to load that HTML and save it as a PDF. We added specific Print CSS (`break-inside: avoid;`) to ensure long tables didn't awkwardly slice a row in half across two pages.

> **Exact AI Prompt Used**: "Act as an expert Python backend engineer. Write `report_generator.py`. Create an HTML template that includes the total orders, total revenue, top 5 products, and a LONG table containing all 200 orders. CRITICAL CSS: Add print CSS `tr { break-inside: avoid; }` and wrap the table header in `<thead>`. Write an async function `generate_pdf()` using Playwright to save it as a PDF."

**Stage 4 & 5: API Endpoints & Idempotency**
We connected the PDF generator to our web server. We created endpoints so that when a user sends a `POST` request, the server builds the PDF, saves it, logs its path in the database, and returns a download link. We also added a safety check: if a report for today already exists, the server instantly returns the existing link instead of building a duplicate.

> **Exact AI Prompt Used**: "Act as an expert Python backend engineer. Update `main.py` to add a `reports` table. Add a `POST /reports` endpoint that runs the pipeline, saves the PDF, and returns a 201 status with the file link. Add a `GET /reports/{id}/file` endpoint using FileResponse. Implement idempotency: if a report for today already exists, DO NOT generate a new PDF; instantly return a 200 OK with the existing link."

**Stage 6: Publish and Document**
The final step was to push the code to GitHub. We created a `.gitignore` file to ensure we didn't accidentally upload the massive PDF files or the local database, and wrote a clear `README.md` explaining how to run the project.

> **Exact AI Prompt Used**: "Act as an expert Python backend engineer. Create a `.gitignore` file that ignores Python cache, our generated `reports/` folder, and our `report.db` file. Create a comprehensive `README.md` file that includes: What this project is, how to run it, the raw SQL query used, proof of the pipeline (curl commands), and an explanation of why idempotency protects server resources."

### Chapter 4: Terminal Testing Guide
To verify the entire pipeline works locally, follow these steps in your terminal:

- **Step 1: Boot the Server** Run `uvicorn main:app --reload` to start the FastAPI server.
- **Step 2: Generate the PDF** Open a *new* terminal window and trigger the pipeline by running `curl -i -X POST http://localhost:8000/reports`. This will take a few seconds as the headless browser renders the file. You will receive a 201 Created response with a JSON file link.
- **Step 3: Test Idempotency** Immediately press your Up Arrow key and run the exact same `curl` command again. The response will be instant. It will return a 200 OK status with the exact same file link, proving the server protected its resources.
- **Step 4: Download the Report** Take the file link from the JSON response and paste it into your web browser (e.g., `http://localhost:8000/reports/1/file`). The browser will automatically download or display the beautifully formatted, multi-page PDF report.
