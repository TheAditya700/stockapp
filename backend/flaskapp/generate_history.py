import mysql.connector
import random
import os

DB_CONFIG = {
    'host': os.environ.get("DATABASE_HOST", "127.0.0.1"),
    'user': "root",
    'password': "linux",
    'database': "stock_app"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def generate_history():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print("Connected to DB. Generating historical completed orders...")

        # Fetch Users
        cursor.execute("SELECT uid FROM User")
        users = [u[0] for u in cursor.fetchall()]

        if len(users) < 2:
            print("Not enough users to generate history.")
            return

        # Fetch Assets (Filter out expensive ones to avoid immediate bankruptcy)
        cursor.execute("SELECT aid, current_price FROM AssetPriceView WHERE current_price < 5000")
        assets = cursor.fetchall()

        if not assets:
            print("No affordable assets found for history generation.")
            return

        transactions_count = 0
        
        # We want every user to have at least a few completed orders.
        # Loop through users to ensure everyone participates
        for uid in users:
            # Make this user BUY 3 times
            for _ in range(3):
                # Pick a random seller (not self)
                seller = random.choice([u for u in users if u != uid])
                
                # Pick random asset
                asset = random.choice(assets)
                aid, price = asset
                
                # Pick random small quantity
                qty = random.randint(1, 5) 
                
                # Insert BUY Order (Pending)
                cursor.execute("""
                    INSERT INTO Orders (uid, aid, price, qty, date, time, otype, status)
                    VALUES (%s, %s, %s, %s, CURDATE(), CURTIME(), 'Buy', 'Pending')
                """, (uid, aid, price, qty))
                
                # Insert SELL Order (Pending) - Matching price to ensure execution
                cursor.execute("""
                    INSERT INTO Orders (uid, aid, price, qty, date, time, otype, status)
                    VALUES (%s, %s, %s, %s, CURDATE(), CURTIME(), 'Sell', 'Pending')
                """, (seller, aid, price, qty))
                
                # Trigger Match
                cursor.execute("CALL MatchOrders()")
                conn.commit()
                transactions_count += 1
        
        # Also make sure everyone SELLS a few times (Short selling logic applies if they don't have it)
        for uid in users:
             for _ in range(2):
                buyer = random.choice([u for u in users if u != uid])
                asset = random.choice(assets)
                aid, price = asset
                qty = random.randint(1, 5)
                
                cursor.execute("""
                    INSERT INTO Orders (uid, aid, price, qty, date, time, otype, status)
                    VALUES (%s, %s, %s, %s, CURDATE(), CURTIME(), 'Buy', 'Pending')
                """, (buyer, aid, price, qty))
                
                cursor.execute("""
                    INSERT INTO Orders (uid, aid, price, qty, date, time, otype, status)
                    VALUES (%s, %s, %s, %s, CURDATE(), CURTIME(), 'Sell', 'Pending')
                """, (uid, aid, price, qty))
                
                cursor.execute("CALL MatchOrders()")
                conn.commit()
                transactions_count += 1

        print(f"Success! Generated {transactions_count} matched historical transactions.")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals() and conn.is_connected(): conn.close()

if __name__ == "__main__":
    generate_history()
