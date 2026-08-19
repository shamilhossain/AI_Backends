import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
from report_data import get_report_data

async def generate_pdf():
    # 1. Fetch the data
    data = get_report_data()
    today_str = datetime.now().strftime("%B %d, %Y")
    
    # 2. Build the HTML string
    # Generate Top Products rows
    top_products_html = ""
    for item in data["top_products"]:
        top_products_html += f"<tr><td>{item['product']}</td><td>${item['revenue']:.2f}</td></tr>"

    # Generate All Orders rows
    all_orders_html = ""
    for order in data["all_orders"]:
        all_orders_html += f"<tr><td>{order['id']}</td><td>{order['customer']}</td><td>{order['product']}</td><td>${order['amount']:.2f}</td><td>{order['date']}</td></tr>"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Sales Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                color: #333;
            }}
            h1, h2 {{
                color: #2c3e50;
            }}
            .summary-box {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 30px;
                border-left: 4px solid #007bff;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 30px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: left;
            }}
            th {{
                background-color: #007bff;
                color: white;
            }}
            /* CRITICAL CSS: prevent row slicing on page breaks */
            tr {{
                break-inside: avoid;
            }}
            /* Ensure the header repeats on every PDF page */
            thead {{
                display: table-header-group;
            }}
        </style>
    </head>
    <body>
        <h1>Sales Report - {today_str}</h1>
        
        <div class="summary-box">
            <h2>Summary</h2>
            <p><strong>Total Orders:</strong> {data['total_orders']}</p>
            <p><strong>Total Revenue:</strong> ${data['total_revenue']:.2f}</p>
        </div>

        <h2>Top 5 Products</h2>
        <table>
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Revenue</th>
                </tr>
            </thead>
            <tbody>
                {top_products_html}
            </tbody>
        </table>

        <h2>All Orders (200 records)</h2>
        <table>
            <thead>
                <tr>
                    <th>Order ID</th>
                    <th>Customer</th>
                    <th>Product</th>
                    <th>Amount</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                {all_orders_html}
            </tbody>
        </table>
    </body>
    </html>
    """

    # 3. Create the reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)

    # 4. Generate the PDF using Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Load the HTML content
        await page.set_content(html_content)
        
        # Save as PDF
        pdf_path = "reports/test.pdf"
        await page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True
        )
        
        await browser.close()
        
    print(f"Successfully generated PDF report at: {pdf_path}")

if __name__ == "__main__":
    asyncio.run(generate_pdf())
