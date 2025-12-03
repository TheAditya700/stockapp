from decimal import Decimal
from datetime import datetime
import random
import mysql.connector

# Database connection setup
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="linux",
    database="stock_app"
)
cursor = db.cursor()

def insert_random_orders():
    # Fetch all users and assets
    cursor.execute("SELECT uid FROM User")
    users = cursor.fetchall()
    
    cursor.execute("SELECT aid, asset_type FROM Asset")
    assets = cursor.fetchall()

    # Prepare to insert random orders
    orders_to_insert = []
    for user in users:
        uid = user[0]

        # Insert a random number of orders for this user
        for _ in range(random.randint(10, 15)):  # Random number of orders between 1 and 5
            # Randomly choose buy or sell order
            otype = random.choice(['Buy', 'Sell'])
            
            # Randomly choose an asset
            asset = random.choice(assets)
            aid = asset[0]
            asset_type = asset[1]

            # Generate random price (within a reasonable range)
            price = round(random.uniform(100, 5000), 2)

            # Generate random quantity
            qty = random.randint(1, 10)  # Random quantity between 1 and 10

            # Insert a random order
            order_data = (uid, aid, qty, price, otype, 'Pending', datetime.now().date(), datetime.now().time())
            orders_to_insert.append(order_data)

    # Bulk insert orders
    cursor.executemany("""
        INSERT INTO Orders (uid, aid, qty, price, otype, status, date, time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, orders_to_insert)
    
    db.commit()
    print(f"Inserted {len(orders_to_insert)} random orders.")

# Run the function
insert_random_orders()

# Close the database connection
cursor.close()
db.close()
