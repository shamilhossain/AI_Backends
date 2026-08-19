import sqlite3
import json

def get_report_data():
    # Connect to the SQLite database
    conn = sqlite3.connect("report.db")
    cursor = conn.cursor()
    
    try:
        # 1. Total Orders
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0] or 0
        
        # 2. Total Revenue
        cursor.execute("SELECT SUM(amount) FROM orders")
        total_revenue = cursor.fetchone()[0] or 0.0
        
        # 3. Top Products by Revenue
        cursor.execute("""
            SELECT product, SUM(amount) as revenue
            FROM orders
            GROUP BY product
            ORDER BY revenue DESC
            LIMIT 5
        """)
        top_products = [
            {"product": row[0], "revenue": round(row[1], 2)}
            for row in cursor.fetchall()
        ]
        
        # 4. Recent Sales (Orders per day for the last 7 days)
        cursor.execute("""
            SELECT date(created_at) as order_date, COUNT(*) as daily_orders
            FROM orders
            WHERE date(created_at) >= date('now', 'localtime', '-7 days')
            GROUP BY order_date
            ORDER BY order_date ASC
        """)
        recent_sales = [
            {"date": row[0], "orders": row[1]}
            for row in cursor.fetchall()
        ]
        
        # Return the aggregated dictionary
        return {
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "top_products": top_products,
            "recent_sales": recent_sales
        }
    
    finally:
        # Ensure the database connection is properly closed
        conn.close()

if __name__ == "__main__":
    report_data = get_report_data()
    print(json.dumps(report_data, indent=4))
