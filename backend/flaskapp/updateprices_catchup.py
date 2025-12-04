import mysql.connector
import random
from datetime import datetime, timedelta

import os

# Database connection setup
# Use environment variable for host if available (e.g. "db" in Docker), else localhost
DB_CONFIG = {
    'host': os.environ.get('DATABASE_HOST', "127.0.0.1"), 
    'user': "root",
    'password': "linux", 
    'database': "stock_app"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def tick():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Get the latest price for EVERY asset
        # We use a correlated subquery or join to find the row with the MAX(date)
        cursor.execute("""
            SELECT p.aid, p.close_price, a.asset_type
            FROM Price p
            JOIN (
                SELECT aid, MAX(date) as max_date
                FROM Price
                GROUP BY aid
            ) latest ON p.aid = latest.aid AND p.date = latest.max_date
            JOIN Asset a ON p.aid = a.aid
        """)
        
        latest_prices = cursor.fetchall()
        
        timestamp = datetime.now().replace(microsecond=0)
        new_entries = []
        
        # 2. Calculate new price for each asset
        for aid, current_price, asset_type in latest_prices:
            current_price = float(current_price)
            
            # Generate random delta
            # Volatility: 0.05% to 0.1% per 10 seconds
            change_percent = random.uniform(-0.001, 0.001)
            
            new_price = current_price * (1 + change_percent)
            
            # Generate OHLC for this 10s bar
            open_p = new_price * (1 + random.uniform(-0.0005, 0.0005))
            high_p = max(open_p, new_price) * (1 + random.uniform(0, 0.0005))
            low_p = min(open_p, new_price) * (1 - random.uniform(0, 0.0005))
            
            # Volume
            if asset_type == 'Commodity':
                 vol = random.randint(10, 500)
            else:
                 vol = random.randint(50, 5000)

            new_entries.append((
                aid, timestamp, 
                round(open_p, 2), round(new_price, 2), 
                round(high_p, 2), round(low_p, 2), 
                vol
            ))
            
        if not new_entries:
            print("No assets found to update.")
            return

        # 3. Insert new prices
        insert_sql = """
            INSERT INTO Price (aid, date, open_price, close_price, high, low, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_sql, new_entries)
        
        # 4. Cleanup: Remove oldest entry for each asset to keep window fixed (e.g. ~360 points)
        # This is a bit expensive to do DELETE with LIMIT per group in MySQL.
        # Alternative: Delete anything older than 1 hour + buffer.
        
        cutoff_time = timestamp - (timedelta(hours=1) + timedelta(minutes=5))
        # Using a simple DELETE based on time is much faster than finding rank per group
        
        # However, the user asked to "pop the oldest value". 
        # Strict "pop" means exactly maintaining count. 
        # Let's try a DELETE older than X approach for efficiency, 
        # assuming the generator runs consistently.
        
        cutoff_timestamp = timestamp - timedelta(minutes=65) # Keep slightly more than 60 mins
        
        cursor.execute("DELETE FROM Price WHERE date < %s", (cutoff_timestamp,))
        
        conn.commit()
        print(f"Tick {timestamp}: Updated {len(new_entries)} assets. Old data cleaned.")
        
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    tick()