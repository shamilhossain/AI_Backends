import os
import re
import time
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone
from pydantic import BaseModel

class BookModel(BaseModel):
    title: str
    product_url: str
    price_gbp: float
    is_in_stock: bool
    rating: int
    description: str | None
    source_page: str
    fetched_at: str

def fetch_html(url: str, filename: str) -> tuple[str, bool]:
    """
    Fetches a URL and caches it locally.
    Returns a tuple of (HTML content, boolean indicating if it was a cache hit).
    """
    cache_dir = Path('cache')
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = cache_dir / filename
    
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read(), True
            
    headers = {
        'User-Agent': 'FlyRankInternship-Scraper/1.0 (+https://github.com/shamilhossain)'
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(response.text)
        
    return response.text, False

def parse_book_page(html_content: str, book_url: str, source_page_url: str) -> dict:
    """
    Parses a single book's HTML page and extracts 8 specific raw fields.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. title
    h1 = soup.find('h1')
    title = h1.text if h1 else None
    
    # 2. product_url
    product_url = book_url
    
    # 3. price_text
    price_p = soup.find('p', class_='price_color')
    price_text = price_p.text if price_p else None
    
    # 4. availability_text
    availability_p = soup.find('p', class_='instock availability')
    availability_text = availability_p.text.strip() if availability_p else None
    
    # 5. rating_text
    rating_p = soup.find('p', class_='star-rating')
    rating_text = " ".join(rating_p.get('class', [])) if rating_p else None
    
    # 6. description
    product_desc_div = soup.find('div', id='product_description')
    description = None
    if product_desc_div:
        desc_p = product_desc_div.find_next_sibling('p')
        if desc_p:
            description = desc_p.text
            
    # 7. source_page
    source_page = source_page_url
    
    # 8. fetched_at
    fetched_at = datetime.now(timezone.utc).isoformat()
    
    return {
        'title': title,
        'product_url': product_url,
        'price_text': price_text,
        'availability_text': availability_text,
        'rating_text': rating_text,
        'description': description,
        'source_page': source_page,
        'fetched_at': fetched_at
    }

def clean_and_validate(raw_book: dict) -> dict:
    """
    Cleans raw extraction data, converts types, and validates using Pydantic.
    """
    # 1. Price -> extract digits and dot, then float
    price_text = raw_book.get('price_text', '')
    clean_price_str = re.sub(r'[^\d.]', '', price_text)
    price_gbp = float(clean_price_str) if clean_price_str else 0.0
    
    # 2. Rating -> text to int
    rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    rating_text = raw_book.get('rating_text', '') or ''
    rating = 0
    for key, val in rating_map.items():
        if key in rating_text:
            rating = val
            break
            
    # 3. Availability -> text to bool
    availability_text = raw_book.get('availability_text', '') or ''
    is_in_stock = 'in stock' in availability_text.lower()
    
    cleaned_data = {
        'title': raw_book.get('title'),
        'product_url': raw_book.get('product_url'),
        'price_gbp': price_gbp,
        'is_in_stock': is_in_stock,
        'rating': rating,
        'description': raw_book.get('description'),
        'source_page': raw_book.get('source_page'),
        'fetched_at': raw_book.get('fetched_at')
    }
    
    # Validate using Pydantic
    book_model = BookModel(**cleaned_data)
    
    # Return validated dictionary
    return book_model.model_dump()

def main():
    base_url = "https://books.toscrape.com/catalogue/"
    book_info_list = []
    
    # Iterate through pages 1, 2, and 3
    for i in range(1, 4):
        url = f"{base_url}page-{i}.html"
        filename = f"catalogue-page-{i}.html"
        
        try:
            html_content, is_cached = fetch_html(url, filename)
            
            # Polite delay
            if not is_cached:
                time.sleep(1)
                
            soup = BeautifulSoup(html_content, 'html.parser')
            articles = soup.find_all('article', class_='product_pod')
            
            for article in articles:
                h3_tag = article.find('h3')
                a_tag = h3_tag.find('a')
                relative_url = a_tag['href']
                absolute_url = urljoin(url, relative_url)
                book_info_list.append((absolute_url, url))
        except Exception as e:
            print(f"Failed to fetch or parse catalogue page {url}. Error: {e}")
            
    print(f"Total book URLs found: {len(book_info_list)}")
    
    # Test the fail-safe: Append a fake URL
    book_info_list.append(("https://books.toscrape.com/catalogue/this-book-does-not-exist.html", "fake-page"))
    print("Injected 1 fake URL for fail-safe testing...")
    
    valid_books = []
    
    # Initialize Counters
    total_attempted = 0
    cache_hits = 0
    valid_records = 0
    failed_pages = 0
    start_time = datetime.now(timezone.utc)
    
    # The Book Loop
    for index, (book_url, source_page_url) in enumerate(book_info_list, start=1):
        total_attempted += 1
        filename = f"book-{index}.html"
        
        try:
            html_content, is_cached = fetch_html(book_url, filename)
            
            if is_cached:
                cache_hits += 1
            else:
                time.sleep(1)
                
            raw_book = parse_book_page(html_content, book_url, source_page_url)
            
            # Clean and validate the raw data
            valid_book = clean_and_validate(raw_book)
            valid_books.append(valid_book)
            valid_records += 1
            
        except Exception as e:
            failed_pages += 1
            print(f"Warning: Failed to process book at {book_url}. Error: {e}")
            continue
        
    # JSON Export
    output_dir = Path('output')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'books.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(valid_books, f, indent=2)
        
    print(f"Successfully saved {len(valid_books)} valid books to {output_file}")
    
    # Generate Run Report
    end_time = datetime.now(timezone.utc)
    duration_seconds = (end_time - start_time).total_seconds()
    
    run_report = {
        "start_time": start_time.isoformat(),
        "duration_seconds": round(duration_seconds, 2),
        "total_attempted": total_attempted,
        "cache_hits": cache_hits,
        "valid_records": valid_records,
        "failed_pages": failed_pages
    }
    
    report_file = output_dir / 'run-report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(run_report, f, indent=2)
        
    print(f"Run report successfully generated and saved to {report_file}")

if __name__ == "__main__":
    main()
