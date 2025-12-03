from werkzeug.security import generate_password_hash
import mysql.connector

# Configure your MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Adjust based on your setup
    password="linux",  # Your MySQL root password
    database="stock_app"
)
cursor = db.cursor()

# Function to hash and update all passwords
def hash_and_update_passwords():
    try:
        # Fetch all users
        cursor.execute("SELECT uid, password FROM `User`")
        users = cursor.fetchall()

        for user in users:
            user_id = user[0]  # Access the uid
            plaintext_password = user[1]  # Access the password

            # Generate hashed password using pbkdf2:sha256 (default)
            hashed_password = generate_password_hash(plaintext_password)

            # Update user password with the hashed version
            cursor.execute("""
                UPDATE `User`
                SET password = %s
                WHERE uid = %s
            """, (hashed_password, user_id))

        # Commit changes to the database
        db.commit()
        print("Passwords successfully hashed and updated!")
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        print(f"Error occurred while updating passwords: {str(e)}")

# Call the function
hash_and_update_passwords()

# Close the cursor and the connection
cursor.close()
db.close()
