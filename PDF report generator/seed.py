import sqlite3
import random
from datetime import datetime, timedelta

def seed_data():
    # 5-6 fake product names
    products = ["Laptop", "Wireless Mouse", "Mechanical Keyboard", "Monitor", "Headphones", "Standing Desk"]

    conn = sqlite3.connect("report.db")
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer TEXT,
            product TEXT,
            amount REAL,
            created_at TEXT
        )
    """)

    # CRITICAL REQUIREMENT: Clear existing data before inserting new rows
    cursor.execute("DELETE FROM orders")

    # Generate 200 random orders
    orders_data = []
    now = datetime.now()
    
    for i in range(200):
        customer = f"Customer_{random.randint(1, 1000)}"
        product = random.choice(products)
        # Random amount between 5 and 200
        amount = round(random.uniform(5.0, 200.0), 2)
        
        # Random date in the last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        seconds_ago = random.randint(0, 59)
        created_at = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago, seconds=seconds_ago)
        created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
        
        orders_data.append((customer, product, amount, created_at_str))

    # Insert exactly 200 random shop orders
    cursor.executemany("""
        INSERT INTO orders (customer, product, amount, created_at)
        VALUES (?, ?, ?, ?)
    """, orders_data)

    conn.commit()
    conn.close()
    
    print("Successfully seeded report.db with 200 random orders.")

if __name__ == "__main__":
    seed_data()
