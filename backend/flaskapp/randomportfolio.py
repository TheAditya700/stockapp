import mysql.connector
import random

# Database connection setup
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="linux",
    database="stock_app"
)
cursor = db.cursor()

def assign_random_portfolio():
    print("Fetching users and assets...")
    
    # Fetch all Portfolios (pid corresponds to a user)
    cursor.execute("SELECT pid, uid FROM Portfolio")
    portfolios = cursor.fetchall() # List of (pid, uid)

    # Fetch all Assets with their current price
    # We use the view to get the latest price easily
    cursor.execute("SELECT aid, current_price FROM AssetPriceView")
    assets = cursor.fetchall() # List of (aid, current_price)

    if not assets:
        print("No assets found. Ensure prices are generated.")
        return

    portfolio_assets_data = []

    print(f"Assigning random assets to {len(portfolios)} portfolios...")

    for pid, uid in portfolios:
        # Decide how many unique assets this user owns (e.g., 3 to 8)
        num_assets = random.randint(3, 8)
        
        # Pick 'num_assets' random assets
        chosen_assets = random.sample(assets, min(num_assets, len(assets)))

        for aid, price in chosen_assets:
            # Random quantity (e.g., 10 to 500)
            qty = random.randint(10, 500)
            
            # Use current price as the "buy_price" for this initial assignment
            # (Simulating they bought it recently at market price)
            buy_price = price

            portfolio_assets_data.append((pid, aid, qty, buy_price))

    # Bulk insert
    sql = """
    INSERT INTO Portfolio_Asset (pid, aid, qty, buy_price)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE qty = qty + VALUES(qty)
    """
    
    # Execute
    cursor.executemany(sql, portfolio_assets_data)
    db.commit()
    
    print(f"Successfully assigned {len(portfolio_assets_data)} asset entries across all portfolios.")

if __name__ == "__main__":
    assign_random_portfolio()
    cursor.close()
    db.close()
