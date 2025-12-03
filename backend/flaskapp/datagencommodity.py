import mysql.connector
import random
from datetime import datetime, timedelta

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

# Function to generate and insert commodity data
def generate_and_insert_commodity(commodity_name, aid):
    start_date = datetime.strptime("2024-05-24", "%Y-%m-%d")
    end_date = datetime.strptime("2024-10-16", "%Y-%m-%d")
    delta = timedelta(days=1)

    # Insert commodity into the Asset table
    cursor.execute("""
        INSERT INTO Asset (aid, name, asset_type)
        VALUES (%s, %s, 'Commodity')
        ON DUPLICATE KEY UPDATE name = VALUES(name), asset_type = 'Commodity';
    """, (aid, commodity_name))
    db.commit()

    # Generate random price data for the commodity
    current_date = start_date
    last_close_price = random.uniform(1500, 2000)
    while current_date <= end_date:
        if current_date.weekday() >= 5:  # Skip weekends
            current_date += delta
            continue

        open_price = last_close_price + random.uniform(-10, 10)
        high = open_price + random.uniform(5, 20)
        low = open_price - random.uniform(5, 20)
        close_price = random.uniform(low, high)
        volume = random.randint(50000, 1000000)

        # Insert price data into the Price table
        cursor.execute("""
            INSERT INTO Price (aid, date, open_price, close_price, high, low, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                open_price = VALUES(open_price),
                close_price = VALUES(close_price),
                high = VALUES(high),
                low = VALUES(low),
                volume = VALUES(volume);
        """, (aid, current_date.strftime("%Y-%m-%d"), round(open_price, 2), round(close_price, 2),
              round(high, 2), round(low, 2), volume))
        db.commit()

        last_close_price = close_price
        current_date += delta

# List of commodities
commodities = ["GOLD", "SILVER", "CRUDE OIL", "NATURAL GAS", "COPPER"]

# Generate and insert data for each commodity
for aid, commodity_name in enumerate(commodities, start=51):
    print(f"Generating data for {commodity_name} (AID: {aid})")
    generate_and_insert_commodity(commodity_name, aid)

# Re-enable foreign key checks
cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
db.commit()

# Close the cursor and connection
cursor.close()
db.close()

print("Commodity data inserted successfully!")
