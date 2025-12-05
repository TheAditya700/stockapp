import mysql.connector
import os
import subprocess
import sys

# Configuration
DB_CONFIG = {
    'host': "127.0.0.1",
    'user': "root",
    'password': "linux",
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def execute_sql_file(cursor, filepath, delimiter=';'):
    print(f"Executing {filepath}...")
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Remove DELIMITER commands as they are client-side
    content = content.replace("DELIMITER $$", "").replace("DELIMITER ;", "")
    
    # Split commands
    if delimiter == '$$':
        commands = content.split('$$')
    else:
        commands = content.split(';')
        
    for cmd in commands:
        cmd = cmd.strip()
        if cmd:
            try:
                cursor.execute(cmd)
            except mysql.connector.Error as err:
                print(f"Error executing command in {filepath}: {err}")
                # Continue despite errors (e.g. dropping non-existent tables)

def main():
    print("--- STARTING FULL RESET ---")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Drop and Recreate Database
        print("Recreating Database...")
        cursor.execute("DROP DATABASE IF EXISTS stock_app")
        cursor.execute("CREATE DATABASE stock_app")
        cursor.execute("USE stock_app")
        
        # 2. Apply Schema
        # We assume we are running from project root or backend, let's handle paths
        base_path = "backend/sql_initialisation"
        if not os.path.exists(base_path):
            # Try relative to current dir if running inside backend
            base_path = "sql_initialisation"
            
        if not os.path.exists(base_path):
            print(f"Error: Could not find sql_initialisation directory at {base_path}")
            sys.exit(1)

        execute_sql_file(cursor, os.path.join(base_path, 'create_tables.sql'), ';')
        execute_sql_file(cursor, os.path.join(base_path, 'function.sql'), '$$')
        execute_sql_file(cursor, os.path.join(base_path, 'procedure.sql'), '$$')
        execute_sql_file(cursor, os.path.join(base_path, 'trigger.sql'), '$$')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database Schema Applied.")
        
        # 3. Run Initialization Script
        print("Running Data Initialization...")
        # Check for initialize.py location
        init_script = "backend/initialize.py"
        if not os.path.exists(init_script):
            init_script = "initialize.py"
            
        if not os.path.exists(init_script):
             print(f"Error: Could not find initialize.py")
             sys.exit(1)
             
        # Run it
        # We run from 'backend' dir so initialize.py finds flaskapp/ correctly
        print(f"Executing initialize.py from backend directory...")
        result = subprocess.run(["python3", "initialize.py"], cwd="backend", capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors during initialization:")
            print(result.stderr)
            
        print("--- RESET COMPLETE ---")
        
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

if __name__ == "__main__":
    main()
