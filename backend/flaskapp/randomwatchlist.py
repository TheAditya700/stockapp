import mysql.connector
import random

# Database connection setup
DB_CONFIG = {
    'host': "127.0.0.1", 
    'user': "root",
    'password': "linux", 
    'database': "stock_app"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Pre-defined themes mapping Names to Assets
THEMES = {
    "Tech Giants": ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM'],
    "Banking Leaders": ['HDFC', 'ICICIBANK', 'HDFCBANK', 'KOTAKBANK', 'AXISBANK', 'SBIN', 'INDUSINDBK'],
    "Auto Sector": ['MARUTI', 'TATAMOTORS', 'HEROMOTOCO', 'EICHERMOT', 'M&M'],
    "Precious Metals & Energy": ['GOLD', 'SILVER', 'CRUDE OIL', 'RELIANCE', 'ONGC'],
    "Heavy Industry": ['LT', 'TATASTEEL', 'JSWSTEEL', 'ULTRACEMCO', 'GRASIM'],
    "Pharma & Health": ['SUNPHARMA', 'DIVISLAB', 'CIPLA', 'DRREDDY', 'APOLLOHOSP'],
    "Adani Group": ['ADANIPORTS', 'ADANIGREEN', 'ADANIENT', 'ADANITRANS']
}

def create_random_watchlists():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("Connected to DB. Creating Random Watchlists...")

    # 1. Fetch Asset IDs mapped by Name
    cursor.execute("SELECT aid, name FROM Asset")
    assets = cursor.fetchall()
    asset_map = {name: aid for aid, name in assets}

    # 2. Fetch Users
    cursor.execute("SELECT uid, uname FROM User")
    users = cursor.fetchall()

    if not users:
        print("No users found!")
        return

    print(f"Assigning watchlists to {len(users)} users...")

    # Prepare data for bulk insert
    watchlist_inserts = []       # (uid, wname)
    watchlist_asset_inserts = [] # (wid, aid) - tricky because we need wid first

    # Since we need the auto-generated WID, we have to insert watchlists one by one or per user
    
    for uid, uname in users:
        # Pick 2 to 4 random themes for this user
        num_themes = random.randint(2, 4)
        chosen_themes = random.sample(list(THEMES.keys()), num_themes)

        for theme_name in chosen_themes:
            # Insert Watchlist
            cursor.execute("INSERT INTO Watchlist (uid, wname) VALUES (%s, %s)", (uid, theme_name))
            wid = cursor.lastrowid

            # Get asset IDs for this theme
            asset_names = THEMES[theme_name]
            for name in asset_names:
                aid = asset_map.get(name)
                if aid:
                    watchlist_asset_inserts.append((wid, aid))
    
    # Bulk insert assets into watchlists
    if watchlist_asset_inserts:
        cursor.executemany("INSERT INTO Watchlist_Asset (wid, aid) VALUES (%s, %s)", watchlist_asset_inserts)
    
    conn.commit()
    print(f"Successfully created watchlists and assigned {len(watchlist_asset_inserts)} asset associations.")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_random_watchlists()
