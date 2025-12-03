from decimal import Decimal
from datetime import datetime, timedelta
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

def update_prices_to_today():
    today = datetime.now().date()

    # Fetch all assets with the latest price details
    cursor.execute("""
        SELECT p.aid, p.date, p.close_price, p.high, p.low
        FROM Price p
        INNER JOIN (
            SELECT aid, MAX(date) AS latest_date
            FROM Price
            GROUP BY aid
        ) latest
        ON p.aid = latest.aid AND p.date = latest.latest_date
    """)
    asset_prices = cursor.fetchall()

    updates = []
    for aid, latest_date, close_price, high, low in asset_prices:
        latest_date = datetime.strptime(str(latest_date), '%Y-%m-%d').date()
        close_price = Decimal(close_price)
        high = Decimal(high)
        low = Decimal(low)

        if latest_date >= today:
            continue

        current_date = latest_date + timedelta(days=1)
        while current_date <= today:
            percent_change = Decimal(random.uniform(-0.02, 0.02))
            new_close_price = round(close_price * (1 + percent_change), 2)
            new_high = round(max(new_close_price, high * (1 + abs(percent_change))), 2)
            new_low = round(min(new_close_price, low * (1 - abs(percent_change))), 2)
            new_open_price = round((new_high + new_low) / 2, 2)
            new_volume = random.randint(50000, 1000000)

            updates.append((aid, current_date, new_open_price, new_close_price, new_high, new_low, new_volume))
            close_price, high, low = new_close_price, new_high, new_low
            current_date += timedelta(days=1)

    for update in updates:
        cursor.execute("""
            INSERT INTO Price (aid, date, open_price, close_price, high, low, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, update)

    db.commit()
    print(f"Inserted {len(updates)} new price entries to catch up to {today}.")

# Run the function
update_prices_to_today()

# Close the database connection
cursor.close()
db.close()
