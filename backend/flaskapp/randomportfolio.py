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

    # Fetch all Assets with their current price and type
    # We use the view to get the latest price easily
    cursor.execute("SELECT aid, current_price, asset_type FROM AssetPriceView")
    assets = cursor.fetchall() # List of (aid, current_price, asset_type)

    if not assets:
        print("No assets found. Ensure prices are generated.")
        return

    # Separate assets by type
    equities = [a for a in assets if a[2] == 'Equity']
    commodities = [a for a in assets if a[2] == 'Commodity']

    portfolio_assets_data = []

    print(f"Assigning random assets to {len(portfolios)} portfolios...")

    for pid, uid in portfolios:
        # Decide how many unique assets this user owns (e.g., 3 to 8)
        num_assets = random.randint(3, 8)
        
        chosen_assets = []
        
        # Ensure at least 1 Equity and 1 Commodity if available
        if equities:
            chosen_assets.append(random.choice(equities))
        if commodities:
            chosen_assets.append(random.choice(commodities))
            
        # Fill the rest randomly from all assets
        remaining_slots = num_assets - len(chosen_assets)
        if remaining_slots > 0:
            # Filter out already chosen ones to avoid duplicates (simplistic approach)
            # strictly speaking sample handles uniqueness from the population, 
            # so we should sample from the full pool excluding what we already picked if we want unique aids.
            # But since random.sample is easy on a list:
            
            # Create a pool of available assets excluding the ones already picked
            picked_aids = {a[0] for a in chosen_assets}
            pool = [a for a in assets if a[0] not in picked_aids]
            
            if pool:
                additional_picks = random.sample(pool, min(remaining_slots, len(pool)))
                chosen_assets.extend(additional_picks)

        for aid, price, asset_type in chosen_assets:
            # Random quantity (e.g., 10 to 500)
            qty = random.randint(10, 500)
            
            # Use current price as the "buy_price" for this initial assignment
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
