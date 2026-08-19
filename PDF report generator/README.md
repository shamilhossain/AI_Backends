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

> **[PLACEHOLDER: Please add a screenshot of the generated PDF here]**
