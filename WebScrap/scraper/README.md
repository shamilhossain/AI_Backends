# Polite Web Scraper

## Target classification
Target: "Books to Scrape" (books.toscrape.com).

Scope: We will only scrape the first 3 catalogue pages.

Purpose: Educational assignment to collect book data.

Robots.txt findings: I manually visited [https://books.toscrape.com/robots.txt](https://books.toscrape.com/robots.txt) and got a "404 Not Found" error. In the web scraping world, this indicates there are no explicit 'disallow' rules and scraping is implicitly allowed (which makes sense for a practice site).

I will not reuse this code on another site without checking its rules and terms first.

## How to Run

To run this project on your local machine, follow these simple step-by-step instructions:

1. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```

2. **Activate the virtual environment:**
   - On macOS/Linux: `source .venv/bin/activate`
   - On Windows: `.venv\Scripts\activate`

3. **Install the required dependencies:**
   ```bash
   pip install requests beautifulsoup4 pydantic
   ```

4. **Run the script:**
   Navigate into the `scraper` folder and run the script:
   ```bash
   cd scraper
   python src/main.py
   ```
   *(Note: The script caches pages locally to prevent spamming the server, making subsequent runs almost instantaneous!)*

## Data Schema

The data extracted by the scraper is strictly validated using a Pydantic schema (`BookModel`). The resulting `books.json` file will contain an array of objects matching this exact structure:

- `title` (str): The exact title of the book.
- `product_url` (str): The absolute URL to the individual book's page.
- `price_gbp` (float): The price of the book in GBP, stripped of any currency symbol.
- `is_in_stock` (bool): `true` if the book is "in stock", otherwise `false`.
- `rating` (int): The star rating of the book mapped to an integer (1 to 5).
- `description` (str | null): The product description text (or null if missing).
- `source_page` (str): The catalogue page URL where this book was found.
- `fetched_at` (str): The ISO 8601 UTC timestamp of when the data was scraped.

## Sample Run Report

To ensure the scraper handles errors gracefully, we implemented a fail-safe test by intentionally injecting a broken URL into the processing queue. The scraper catches the `404 Not Found` error, logs it as a warning, and continues extracting the legitimate books without crashing.

Here is the exact `run-report.json` generated from our latest run, proving the resilience of the script:

```json
{
  "start_time": "2026-08-12T14:15:17.867144+00:00",
  "duration_seconds": 1.06,
  "total_attempted": 61,
  "cache_hits": 60,
  "valid_records": 60,
  "failed_pages": 1
}
```
