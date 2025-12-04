import mysql.connector
import random
from datetime import datetime, timedelta

# --- CONFIGURATION ---
DB_CONFIG = {
    'host': "127.0.0.1", 
    'user': "root",
    'password': "linux", 
    'database': "stock_app"
}

# 1. Define Data Sources
EQUITIES = [
    'RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICIBANK', 'HINDUNILVR', 'HDFCBANK', 'BAJFINANCE', 
    'KOTAKBANK', 'BHARTIARTL', 'ITC', 'LT', 'AXISBANK', 'ASIANPAINT', 'SBIN', 'MARUTI', 
    'ULTRACEMCO', 'SUNPHARMA', 'NTPC', 'TITAN', 'WIPRO', 'M&M', 'HCLTECH', 'NESTLEIND', 
    'TECHM', 'POWERGRID', 'ADANIPORTS', 'HDFCLIFE', 'COALINDIA', 'JSWSTEEL', 'BRITANNIA', 
    'GRASIM', 'BPCL', 'DIVISLAB', 'CIPLA', 'ONGC', 'BAJAJFINSV', 'TATASTEEL', 'DRREDDY', 
    'HEROMOTOCO', 'TATAMOTORS', 'INDUSINDBK', 'SBILIFE', 'SHREECEM', 'EICHERMOT', 'UPL', 
    'APOLLOHOSP', 'ADANIGREEN', 'ADANIENT', 'ADANITRANS'
]

COMMODITIES = ["GOLD", "SILVER", "CRUDE OIL", "NATURAL GAS", "COPPER"]

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def generate_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("Connected to DB. Starting High-Frequency Generation...")

    # --- STEP 0: Clean Slate ---
    print("Clearing existing Price and Asset data...")
    cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
    cursor.execute("TRUNCATE TABLE Price")
    cursor.execute("TRUNCATE TABLE Asset")
    cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
    conn.commit()

    # --- STEP 1: Insert Assets ---
    print("Creating Assets...")
    
    # Insert Equities
    for name in EQUITIES:
        cursor.execute("""
            INSERT INTO Asset (name, asset_type) VALUES (%s, 'Equity') 
        """, (name,))

    # Insert Commodities
    for name in COMMODITIES:
        cursor.execute("""
            INSERT INTO Asset (name, asset_type) VALUES (%s, 'Commodity') 
        """, (name,))
    
    conn.commit()

    # --- STEP 2: Generate Prices (Last 1 Hour, every 10 seconds) ---
    # 1 hour = 3600 seconds. 10 second intervals = 360 points.
    
    print("Generating 1 hour of history (10s intervals) for ALL assets...")
    
    # Fetch all assets (both types) from DB to get their correct auto-generated IDs
    cursor.execute("SELECT aid, name, asset_type FROM Asset")
    all_assets = cursor.fetchall()

    # End time is NOW
    end_time = datetime.now()
    # Round to nearest 10s for cleanliness
    end_time = end_time.replace(microsecond=0, second=(end_time.second // 10) * 10)

    batch_data = []
    total_points = 360 # 1 hour / 10 seconds

    for aid, name, asset_type in all_assets:
        # Set base price based on type for realism
        if asset_type == 'Commodity':
            if name == 'GOLD': current_price = 60000
            elif name == 'SILVER': current_price = 7000
            else: current_price = random.uniform(2000, 5000)
        else:
            current_price = random.uniform(100, 3000) # Equities

        # Generate points backwards from now
        for i in range(total_points, -1, -1):
            # Time point: i intervals ago
            timestamp = end_time - timedelta(seconds=i*10)
            
            # Random Fluctuation (smaller for 10s intervals)
            # Volatility per 10s should be small, e.g., 0.05% to 0.2%
            change_percent = random.uniform(-0.001, 0.001) 
            current_price = current_price * (1 + change_percent)
            
            # Create OHLC bars for the 10s interval (micro-movements)
            open_p = current_price * (1 + random.uniform(-0.0005, 0.0005))
            high_p = max(open_p, current_price) * (1 + random.uniform(0, 0.0005))
            low_p = min(open_p, current_price) * (1 - random.uniform(0, 0.0005))
            
            # Volume
            if asset_type == 'Commodity':
                 vol = random.randint(10, 500)
            else:
                 vol = random.randint(50, 5000)

            # Add to batch
            batch_data.append((
                aid, timestamp, 
                round(open_p, 2), round(current_price, 2), 
                round(high_p, 2), round(low_p, 2), 
                vol
            ))

    # --- STEP 3: Bulk Insert ---
    print(f"Inserting {len(batch_data)} price records...")
    
    sql = """
        INSERT INTO Price (aid, date, open_price, close_price, high, low, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    # Insert in chunks of 5000
    chunk_size = 5000
    for i in range(0, len(batch_data), chunk_size):
        cursor.executemany(sql, batch_data[i:i + chunk_size])
        conn.commit()
        print(f"   Inserted batch {i} to {i+chunk_size}...")

    print("Success! Database populated with high-frequency data.")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    generate_data()
