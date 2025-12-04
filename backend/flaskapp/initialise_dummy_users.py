import mysql.connector
import os
from werkzeug.security import generate_password_hash

# 1. Configure your MySQL connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DATABASE_HOST", "127.0.0.1"),
        user="root",        # Adjust if needed
        password="linux",   # Your MySQL root password
        database="stock_app"
    )

# 2. Define the Dummy Data (Address + User paired together)
# format: (Address Data Tuple, User Data Tuple)
dummy_data = [
    (
        ('MG Road', 'Bangalore', 'Brigade Towers', '12'),
        ('Amit Sharma', 'amit.sharma@example.com', '9876543210', 10000.00, 5000.00)
    ),
    (
        ('Andheri', 'Mumbai', 'Sea Breeze Apartments', '23B'),
        ('Priya Patel', 'priya.patel@example.com', '9876543211', 15000.00, 3000.00)
    ),
    (
        ('Salt Lake', 'Kolkata', 'Infinity Towers', '45A'),
        ('Priyansh Gupta', 'priyansh.gupta@example.com', '9876543212', 20000.00, 1000.00)
    ),
    (
        ('Jubilee Hills', 'Hyderabad', 'Sunrise Residency', '67'),
        ('Anjali Nair', 'anjali.nair@example.com', '9876543213', 12000.00, 2000.00)
    ),
    (
        ('Connaught Place', 'Delhi', 'Royal Apartments', '34'),
        ('Vikram Mehta', 'vikram.mehta@example.com', '9876543214', 18000.00, 4000.00)
    ),
    (
        ('Viman Nagar', 'Pune', 'Skyline Towers', '22'),
        ('Deepika Rao', 'deepika.rao@example.com', '9876543215', 13000.00, 3500.00)
    ),
    (
        ('Banjara Hills', 'Hyderabad', 'Hilltop Villas', '101'),
        ('Rohan Kallumal', 'rohan.k@example.com', '9876543216', 22000.00, 2500.00)
    ),
    (
        ('Sector 18', 'Noida', 'Silver Residency', '89'),
        ('Simran Singh', 'simran.singh@example.com', '9876543217', 16000.00, 4500.00)
    ),
    (
        ('Park Street', 'Kolkata', 'Galaxy Towers', '56A'),
        ('Karan Desai', 'karan.desai@example.com', '9876543218', 17500.00, 5000.00)
    ),
    (
        ('Koramangala', 'Bangalore', 'Eagle Apartments', '77'),
        ('Neha Verma', 'neha.verma@example.com', '9876543219', 14000.00, 1500.00)
    )
]

def insert_dummy_users_with_hashes():
    try:
        db = get_db_connection()
        cursor = db.cursor()
        print("Connected to database successfully.")

        # Clean slate
        print("Clearing existing Users and Addresses...")
        cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        cursor.execute("TRUNCATE TABLE User")
        cursor.execute("TRUNCATE TABLE Address")
        cursor.execute("TRUNCATE TABLE Portfolio") # Portfolio is created by trigger, so clear it too
        cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
        db.commit()

        # We use a default password for all dummy users for simplicity
        raw_password = "password123"
        
        # Hash it once (or move inside loop if you want different salts per user, 
        # though generate_password_hash handles salt automatically)
        hashed_password = generate_password_hash(raw_password)

        print(f"Preparing to insert {len(dummy_data)} users...")

        for addr, user in dummy_data:
            # --- Step 1: Insert Address ---
            sql_address = """
                INSERT INTO Address (locality, city, building, hno) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql_address, addr)
            
            # Get the auto-generated address_id from the insert above
            new_address_id = cursor.lastrowid

            # --- Step 2: Insert User ---
            # Unpack user data
            uname, uemail, upno, equity, commodity = user

            sql_user = """
                INSERT INTO User (uname, uemail, upno, equity_funds, commodity_funds, address_id, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            val_user = (uname, uemail, upno, equity, commodity, new_address_id, hashed_password)
            
            cursor.execute(sql_user, val_user)
            print(f"Inserted User: {uname} (Linked to Address ID: {new_address_id})")

        # Commit all changes
        db.commit()
        print("\nAll dummy users and addresses inserted successfully!")
        print(f"Default password for all users is: {raw_password}")

    except mysql.connector.Error as err:
        # Rollback in case of error to keep DB clean
        if 'db' in locals() and db.is_connected():
             db.rollback()
        print(f"Error: {err}")
    except Exception as e:
        if 'db' in locals() and db.is_connected():
             db.rollback()
        print(f"Unexpected Error: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'db' in locals() and db.is_connected(): db.close()
        print("Database connection closed.")

if __name__ == "__main__":
    insert_dummy_users_with_hashes()