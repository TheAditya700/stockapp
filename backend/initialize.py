import time
import os
import mysql.connector
import subprocess

DB_CONFIG = {
    'host': os.environ.get("DATABASE_HOST", "127.0.0.1"),
    'user': "root",
    'password': "linux",
    'database': "stock_app"
}

def wait_for_db():
    print("Waiting for database connection...")
    retries = 30
    while retries > 0:
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            conn.close()
            print("Database is ready!")
            return True
        except mysql.connector.Error:
            time.sleep(1)
            retries -= 1
    print("Could not connect to database.")
    return False

def check_if_initialized():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM User")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except mysql.connector.Error:
        return False

def run_script(script_name):
    print(f"Running {script_name}...")
    # Assuming scripts are in flaskapp/ directory relative to where this script runs
    # We are running from /app in the container, so scripts are in flaskapp/
    path = os.path.join("flaskapp", script_name)
    result = subprocess.run(["python3", path], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Success: {script_name}")
        print(result.stdout)
    else:
        print(f"Error running {script_name}:")
        print(result.stderr)

def main():
    if not wait_for_db():
        return

    if check_if_initialized():
        print("Database already contains users. Skipping initialization.")
    else:
        print("Database is empty (no users). Starting initialization sequence...")
        
        scripts = [
            "datagen_assets.py",         # 1. Assets & Commodities & Prices
            "initialise_dummy_users.py", # 2. Users & Addresses & Portfolios
            "randomportfolio.py",        # 3. Portfolio Holdings
            "randomorders.py",           # 4. Orders & Matching
            "generate_history.py",       # 5. Guaranteed Completed Orders (History)
            "randomwatchlist.py"         # 6. Watchlists
        ]
        
        for script in scripts:
            run_script(script)
            
        print("Initialization sequence complete.")

if __name__ == "__main__":
    main()
