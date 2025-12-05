import mysql.connector
import subprocess
import os
import sys
import time

# Configuration
DB_CONFIG = {
    'host': "127.0.0.1",
    'user': "root",
    'password': "linux",
    'database': "stock_app"
}

def get_db_connection(db_name=None):
    config = DB_CONFIG.copy()
    if db_name:
        config['database'] = db_name
    else:
        del config['database'] # Connect without DB to drop/create
    return mysql.connector.connect(**config)

def execute_sql_script(cursor, filepath, delimiter=';'):
    print(f"Executing SQL script: {filepath}")
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Remove DELIMITER statements as they are client-side
    content = content.replace("DELIMITER $$", "").replace("DELIMITER ;", "")
    
    if delimiter == '$$':
        statements = content.split('$$')
    else:
        statements = content.split(';')
        
    for statement in statements:
        stmt = statement.strip()
        if stmt:
            try:
                cursor.execute(stmt)
            except mysql.connector.Error as err:
                print(f"Error executing statement: {stmt[:50]}...\nError: {err}")
                # Don't exit, some might be harmless warnings or drops
                
def setup_database():
    print("--- Setting up Database ---")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Drop and Create DB
    cursor.execute("DROP DATABASE IF EXISTS stock_app")
    cursor.execute("CREATE DATABASE stock_app")
    cursor.execute("USE stock_app")
    
    # Execute Create Tables
    execute_sql_script(cursor, 'sql_initialisation/create_tables.sql', ';')
    
    # Execute Functions, Procedures, Triggers
    # These use $$ delimiter in the file, but we stripped the DELIMITER command.
    # We should split by $$ because the file structure implies it.
    execute_sql_script(cursor, 'sql_initialisation/function.sql', '$$')
    execute_sql_script(cursor, 'sql_initialisation/procedure.sql', '$$')
    execute_sql_script(cursor, 'sql_initialisation/trigger.sql', '$$')
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Database setup complete.")

def run_initialization_script():
    print("--- Running Initialization Script ---")
    # Run initialize.py using subprocess. 
    # It expects to be in backend/ (based on relative paths to flaskapp/...)
    # We assume this script is running from backend/ directory or we handle paths.
    
    # Check if initialize.py is in current dir
    if os.path.exists("initialize.py"):
        cmd = ["python3", "initialize.py"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("Initialization failed:")
            print(result.stderr)
            sys.exit(1)
        else:
            print("Initialization Output:")
            print(result.stdout)
    else:
        print("Error: initialize.py not found in current directory.")
        sys.exit(1)

def get_user_balance(cursor, uid):
    cursor.execute("SELECT equity_funds, commodity_funds FROM User WHERE uid = %s", (uid,))
    return cursor.fetchone()

def get_portfolio_qty(cursor, uid, aid):
    # Get PID first
    cursor.execute("SELECT pid FROM Portfolio WHERE uid = %s", (uid,))
    pid = cursor.fetchone()[0]
    cursor.execute("SELECT qty FROM Portfolio_Asset WHERE pid = %s AND aid = %s", (pid, aid))
    res = cursor.fetchone()
    return res[0] if res else 0

def get_pending_cost(cursor, uid):
    cursor.execute("SELECT GetTotalPendingCostEquity(%s)", (uid,))
    res = cursor.fetchone()
    return float(res[0]) if res and res[0] else 0.0

def run_tests():
    print("\n--- Starting Tests ---")
    conn = get_db_connection("stock_app")
    cursor = conn.cursor()

    # 1. Setup Test Data
    # Get two users
    cursor.execute("SELECT uid, uname, equity_funds FROM User LIMIT 2")
    users = cursor.fetchall()
    u1_id, u1_name, u1_initial_funds = users[0]
    u2_id, u2_name, u2_initial_funds = users[1]
    
    # Delete any existing pending orders for the test users
    cursor.execute("DELETE FROM Orders WHERE uid IN (%s, %s) AND status = 'Pending'", (u1_id, u2_id))
    conn.commit()
    print(f"Cleared pending orders for User {u1_id} and User {u2_id}.")


    # Get an Equity Asset
    cursor.execute("SELECT aid, name, current_price FROM AssetPriceView WHERE asset_type='Equity' LIMIT 1")
    asset = cursor.fetchone()
    aid, aname, price = asset
    print(f"Asset: {aname} (ID: {aid}), Price: {price}")
    
    price = float(price)
    u1_initial_funds = float(u1_initial_funds)
    u2_initial_funds = float(u2_initial_funds)

    # Ensure Users have enough funds
    required_funds = 10 * price
    if u1_initial_funds < required_funds:
        print(f"Topup User 1 with {required_funds}")
        cursor.execute("UPDATE User SET equity_funds = equity_funds + %s WHERE uid = %s", (required_funds, u1_id))
        u1_initial_funds += required_funds
        conn.commit()
        
    # --- TEST CASE 1: Place BUY Order (Pending) ---
    print("\n[Test 1] Placing BUY Order (Qty: 10)...")
    cursor.execute("CALL place_order(%s, %s, %s, 'Buy')", (u1_id, aid, 10))
    conn.commit()
    
    # Verify Pending Cost
    pending_cost = get_pending_cost(cursor, u1_id)
    expected_cost = 10 * price
    print(f"Pending Cost: {pending_cost}, Expected: {expected_cost}")
    assert abs(pending_cost - expected_cost) < 0.01, "Pending Cost Mismatch"
    
    # Verify Funds NOT deducted yet
    curr_funds = float(get_user_balance(cursor, u1_id)[0])
    print(f"User 1 Funds: {curr_funds}, Expected: {u1_initial_funds}")
    assert abs(curr_funds - u1_initial_funds) < 0.01, "Funds should not be deducted for Pending Order"

    # --- TEST CASE 2: Place SELL Order (Partial Match - Qty 5) ---
    print("\n[Test 2] Placing SELL Order (Qty: 5)...")
    cursor.execute("CALL place_order(%s, %s, %s, 'Sell')", (u2_id, aid, 5))
    conn.commit()
    
    print("Matching Orders...")
    cursor.execute("CALL MatchOrders()")
    conn.commit()
    
    # Verify Transaction
    cursor.execute("SELECT qty, price FROM Transaction WHERE buy_uid=%s AND sell_uid=%s ORDER BY tid DESC LIMIT 1", (u1_id, u2_id))
    trans = cursor.fetchone()
    assert trans is not None, "Transaction not found"
    t_qty, t_price = trans
    print(f"Transaction: Qty {t_qty}, Price {t_price}")
    assert t_qty == 5, "Transaction Qty mismatch"
    
    # Verify User 1 Funds (Deducted for 5)
    curr_funds_u1 = float(get_user_balance(cursor, u1_id)[0])
    expected_funds_u1 = u1_initial_funds - (5 * price)
    print(f"User 1 Funds: {curr_funds_u1}, Expected: {expected_funds_u1}")
    assert abs(curr_funds_u1 - expected_funds_u1) < 0.01, "User 1 Funds Mismatch after partial match"
    
    # Verify User 2 Funds (Added for 5)
    curr_funds_u2 = float(get_user_balance(cursor, u2_id)[0])
    expected_funds_u2 = u2_initial_funds + (5 * price)
    print(f"User 2 Funds: {curr_funds_u2}, Expected: {expected_funds_u2}")
    assert abs(curr_funds_u2 - expected_funds_u2) < 0.01, "User 2 Funds Mismatch after partial match"
    
    # Verify Portfolios
    u1_qty = get_portfolio_qty(cursor, u1_id, aid)
    u2_qty = get_portfolio_qty(cursor, u2_id, aid)
    print(f"User 1 Portfolio Qty: {u1_qty} (Expected increase +5)")
    print(f"User 2 Portfolio Qty: {u2_qty} (Expected decrease -5)")
    
    # Verify Pending Cost (Should be for remaining 5)
    pending_cost = get_pending_cost(cursor, u1_id)
    expected_pending = 5 * price
    print(f"Remaining Pending Cost: {pending_cost}, Expected: {expected_pending}")
    assert abs(pending_cost - expected_pending) < 0.01, "Pending Cost Mismatch after partial match"

    # --- TEST CASE 3: Place SELL Order (Remaining Match - Qty 5) ---
    print("\n[Test 3] Placing SELL Order (Qty: 5) to match remaining...")
    cursor.execute("CALL place_order(%s, %s, %s, 'Sell')", (u2_id, aid, 5))
    conn.commit()
    
    print("Matching Orders...")
    cursor.execute("CALL MatchOrders()")
    conn.commit()
    
    # Verify Orders Cleared
    cursor.execute("SELECT count(*) FROM Orders WHERE uid=%s AND status='Pending'", (u1_id,))
    pending_count = cursor.fetchone()[0]
    print(f"User 1 Pending Orders: {pending_count}")
    assert pending_count == 0, "User 1 should have no pending orders"
    
    # Verify User 1 Funds (Deducted for full 10)
    curr_funds_u1 = float(get_user_balance(cursor, u1_id)[0])
    expected_funds_u1 = u1_initial_funds - (10 * price)
    print(f"User 1 Final Funds: {curr_funds_u1}, Expected: {expected_funds_u1}")
    assert abs(curr_funds_u1 - expected_funds_u1) < 0.01, "User 1 Final Funds Mismatch"
    
    print("\nALL TESTS PASSED SUCCESSFULLY!")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    # Ensure we are in backend/ directory
    if os.path.basename(os.getcwd()) != 'backend':
        if os.path.exists('backend'):
            os.chdir('backend')
        else:
            print("Please run from project root or backend directory.")
            sys.exit(1)

    setup_database()
    run_initialization_script()
    run_tests()
