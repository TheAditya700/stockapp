import mysql.connector
import random

# Configure your MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="linux",
    database="stock_app"
)
cursor = db.cursor()

# Disable foreign key checks temporarily
cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
db.commit()

# Fetch all portfolios
cursor.execute("SELECT pid FROM Portfolio;")
portfolio_ids = [row[0] for row in cursor.fetchall()]

# Fetch all commodity IDs
cursor.execute("SELECT aid FROM Asset WHERE asset_type = 'Commodity';")
commodity_ids = [row[0] for row in cursor.fetchall()]

# Randomly assign commodities to portfolios
assignments = []
for portfolio_id in portfolio_ids:
    # Assign a random number of commodities (between 1 and 3) to this portfolio
    num_commodities = random.randint(1, 3)
    assigned_commodities = random.sample(commodity_ids, num_commodities)
    for commodity_id in assigned_commodities:
        # Random quantity between 1 and 10
        quantity = random.randint(1, 10)
        # Random buy price between 100 and 1000
        buy_price = round(random.uniform(100, 1000), 2)
        assignments.append((portfolio_id, commodity_id, quantity, buy_price))

# Insert into Portfolio_Asset table
for portfolio_id, commodity_id, quantity, buy_price in assignments:
    cursor.execute("""
        INSERT INTO Portfolio_Asset (pid, aid, qty, buy_price)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE qty = qty + VALUES(qty)
    """, (portfolio_id, commodity_id, quantity, buy_price))

db.commit()

# Enable foreign key checks again
cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
db.commit()

# Close the cursor and connection
cursor.close()
db.close()

print("Commodities have been successfully assigned to portfolios!")
