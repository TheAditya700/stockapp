import requests
import mysql.connector
from datetime import datetime
import time

# Configure your MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Adjust based on your setup
    password="linux",  # Your MySQL root password
    database="stock_app"
)
cursor = db.cursor()

# Alpha Vantage API key
API_KEY = 'HRAKSZKWQIQE93BD'

# List of NIFTY 50 stock symbols with BSE
symbols = ['TECHM', 'POWERGRID', 'ADANIPORTS', 'HDFCLIFE', 
           'COALINDIA', 'JSWSTEEL', 'BRITANNIA', 'GRASIM', 'BPCL', 'DIVISLAB', 'CIPLA', 'ONGC', 'BAJAJFINSV', 
           'TATASTEEL', 'DRREDDY', 'HEROMOTOCO', 'TATAMOTORS', 'INDUSINDBK', 'SBILIFE', 'SHREECEM', 'EICHERMOT', 
           'UPL', 'APOLLOHOSP', 'ADANIGREEN', 'ADANIENT', 'ADANITRANS']


# Function to fetch historical data for each stock symbol
def fetch_and_insert_data(symbol):
    print(f"Fetching data for {symbol}")
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}.BSE&apikey={API_KEY}&outputsize=compact'
    response = requests.get(url)

    try:
        data = response.json()
    except ValueError:
        print(f"Error decoding JSON for {symbol}")
        return

    if 'Time Series (Daily)' not in data:
        print(f"Data for {symbol} not available or API limit exceeded.")
        return

    time_series = data['Time Series (Daily)']

    # Fetch the asset ID (aid) once for this stock
    cursor.execute("SELECT aid FROM Asset WHERE name = %s", (symbol,))
    result = cursor.fetchone()  # Fetch the result
    if result is None:
        print(f"No asset ID found for {symbol}")
        return

    aid = result[0]  # Extract the aid

    # Close the previous result set to avoid unread result error
    cursor.fetchall()  # If there are multiple rows, fetch them all to clear the result set

    # Loop over each date and insert into the Price table
    for date_str, daily_data in time_series.items():
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        open_price = float(daily_data['1. open'])
        high_price = float(daily_data['2. high'])
        low_price = float(daily_data['3. low'])
        close_price = float(daily_data['4. close'])
        volume = int(daily_data['5. volume'])

        # Insert into the Price table
        cursor.execute("""
            INSERT INTO Price (aid, date, open_price, close_price, high, low, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                open_price = VALUES(open_price),
                close_price = VALUES(close_price),
                high = VALUES(high),
                low = VALUES(low),
                volume = VALUES(volume)
        """, (aid, date, open_price, close_price, high_price, low_price, volume))

    # Commit after each stock's data is inserted
    db.commit()

# Fetch and insert data for all symbols
for symbol in symbols:
    fetch_and_insert_data(symbol)
    time.sleep(13)  # Throttle the requests to avoid hitting API rate limits

# Close the cursor and connection
cursor.close()
db.close()

print("Data inserted successfully for all NIFTY 50 stocks!")
