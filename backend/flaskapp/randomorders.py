import os
import mysql.connector
from datetime import datetime
from decimal import Decimal
import random

# Database connection setup
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DATABASE_HOST", "127.0.0.1"),
        user="root",
        password="linux",
        database="stock_app"
    )

def insert_random_orders():
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        print("Fetching user funds and portfolio holdings...")
        # Fetch all users with their funds
        cursor.execute("SELECT uid, equity_funds, commodity_funds FROM User")
        users_data = cursor.fetchall()
        users_funds = {u[0]: {'equity': u[1], 'commodity': u[2]} for u in users_data}
        
        # Fetch all assets with their types
        cursor.execute("SELECT aid, asset_type FROM Asset")
        assets_data = cursor.fetchall()
        assets_info = {a[0]: {'type': a[1]} for a in assets_data}
        
        equity_ids = [aid for aid, info in assets_info.items() if info['type'] == 'Equity']
        commodity_ids = [aid for aid, info in assets_info.items() if info['type'] == 'Commodity']

        # Fetch all portfolio holdings (pid, aid, qty)
        cursor.execute("SELECT pid, aid, qty FROM Portfolio_Asset")
        portfolio_assets_data = cursor.fetchall()

        # Map uids to pids
        cursor.execute("SELECT pid, uid FROM Portfolio")
        uid_to_pid_map = {p[1]: p[0] for p in cursor.fetchall()}

        # Organize holdings by user and asset
        users_holdings = {}
        for pid, aid, qty in portfolio_assets_data:
            current_uid = next((uid for uid, p_id in uid_to_pid_map.items() if p_id == pid), None)
            if current_uid:
                if current_uid not in users_holdings:
                    users_holdings[current_uid] = {}
                users_holdings[current_uid][aid] = qty

        # Prepare to insert random orders
        orders_to_insert = []
        # Use a set to keep track of assets available for selling per user, to avoid selling what they don't have
        
        print("Generating random orders with limits...")
        for uid, funds in users_funds.items():
            user_portfolio = users_holdings.get(uid, {})

            # Insert a random number of orders for this user
            for _ in range(random.randint(5, 10)): # Reduced range for number of orders
                otype = random.choice(['Buy', 'Sell'])
                
                # Decide whether to trade Equity or Commodity (50/50 chance if both exist)
                target_type = random.choice(['Equity', 'Commodity'])
                
                # Select valid asset IDs based on target type
                if target_type == 'Equity' and equity_ids:
                    aid = random.choice(equity_ids)
                elif target_type == 'Commodity' and commodity_ids:
                    aid = random.choice(commodity_ids)
                elif equity_ids: # Fallback if no commodities
                    aid = random.choice(equity_ids)
                elif commodity_ids: # Fallback if no equities
                    aid = random.choice(commodity_ids)
                else:
                    continue # No assets available

                asset_type = assets_info[aid]['type']

                # Generate random price (within a reasonable range)
                price = round(random.uniform(50, 1000), 2) # Adjusted price range

                # Determine max quantity based on funds for Buy or holdings for Sell
                max_qty_for_order = 0
                
                if otype == 'Buy':
                    available_funds = funds['equity'] if asset_type == 'Equity' else funds['commodity']
                    if price > 0 and available_funds > 0:
                        max_qty_for_order = int(available_funds / Decimal(str(price)))
                    
                elif otype == 'Sell':
                    max_qty_for_order = user_portfolio.get(aid, 0)
                
                # Ensure a minimum quantity of 1 for the random generation
                # Limit the random quantity to a more reasonable range, e.g., 1 to 5 units, or max_qty_for_order
                qty_upper_bound = min(5, max_qty_for_order if max_qty_for_order > 0 else 0)
                
                if qty_upper_bound < 1: # Cannot place order if max possible quantity is 0
                    continue

                qty = random.randint(1, qty_upper_bound)
                
                if qty > 0: # Only add order if quantity is positive
                    order_data = (uid, aid, qty, price, otype, 'Pending', datetime.now().date(), datetime.now().time())
                    orders_to_insert.append(order_data)

        # Bulk insert orders
        cursor.executemany("""
            INSERT INTO Orders (uid, aid, qty, price, otype, status, date, time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, orders_to_insert)
        
        db.commit()
        print(f"Inserted {len(orders_to_insert)} random orders.")

        # Run MatchOrders procedure to execute trades
        print("Matching orders...")
        cursor.execute("CALL MatchOrders()")
        db.commit()
        print("Orders matched.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'db' in locals() and db.is_connected(): db.close()

if __name__ == "__main__":
    insert_random_orders()
