from flask import Blueprint, jsonify, request, abort
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from extensions import db

from datetime import datetime, timedelta
import random
from decimal import Decimal

def update_prices_to_today():
    today = datetime.now().date()

    # Fetch all assets with their latest price details
    result = db.session.execute("""
        SELECT p.aid, p.date, p.close_price, p.high, p.low
        FROM Price p
        INNER JOIN (
            SELECT aid, MAX(date) AS latest_date
            FROM Price
            GROUP BY aid
        ) latest
        ON p.aid = latest.aid AND p.date = latest.latest_date
    """)
    asset_prices = result.fetchall()

    updates = []
    for aid, latest_date, close_price, high, low in asset_prices:
        latest_date = latest_date.date()
        close_price = Decimal(close_price)
        high = Decimal(high)
        low = Decimal(low)

        # If prices are already up to date, skip
        if latest_date >= today:
            continue

        # Update prices for missing dates
        current_date = latest_date + timedelta(days=1)
        while current_date <= today:
            percent_change = Decimal(random.uniform(-0.02, 0.02))  # +/- 2% change
            new_close_price = round(close_price * (1 + percent_change), 2)
            new_high = round(max(new_close_price, high * (1 + abs(percent_change))), 2)
            new_low = round(min(new_close_price, low * (1 - abs(percent_change))), 2)
            new_open_price = round((new_high + new_low) / 2, 2)
            new_volume = random.randint(50000, 1000000)

            updates.append((aid, current_date, new_open_price, new_close_price, new_high, new_low, new_volume))

            # Prepare for the next day's data
            close_price, high, low = new_close_price, new_high, new_low
            current_date += timedelta(days=1)

    # Insert updated prices into the database
    for update in updates:
        db.session.execute("""
            INSERT INTO Price (aid, date, open_price, close_price, high, low, volume)
            VALUES (:aid, :date, :open_price, :close_price, :high, :low, :volume)
        """, {
            'aid': update[0],
            'date': update[1],
            'open_price': update[2],
            'close_price': update[3],
            'high': update[4],
            'low': update[5],
            'volume': update[6],
        })

    db.session.commit()
    print(f"Updated prices for {len(updates)} entries up to {today}.")


user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/register', methods=['POST'])
def register_user():
    try:
        print("--- STARTING REGISTRATION ---")
        data = request.get_json()
        
        # 1. Validate Input Data
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
            
        uname = data.get('uname')
        uemail = data.get('uemail')
        password = data.get('password')
        address = data.get('address') # Expecting a nested dict

        if not all([uname, uemail, password, address]):
            print("Missing fields:", data)
            return jsonify({"error": "Missing required fields (uname, uemail, password, address)"}), 400

        # 2. Check if User Exists
        print(f"Checking if user {uemail} exists...")
        user_exist = db.session.execute(
            text("SELECT uid FROM `User` WHERE uemail = :email"), 
            {'email': uemail}
        ).fetchone()
        
        if user_exist:
            return jsonify({"error": "User already exists"}), 409

        # 3. Insert Address
        print("Inserting Address...")
        sql_insert_address = text("""
            INSERT INTO Address (locality, city, building, hno) 
            VALUES (:locality, :city, :building, :hno)
        """)
        
        # Safe .get() to avoid crashing if fields are missing inside address
        db.session.execute(sql_insert_address, {
            'locality': address.get('locality', ''),
            'city': address.get('city', ''),
            'building': address.get('building', ''),
            'hno': address.get('hno', '')
        })
        
        # Get the ID of the address we just inserted
        address_id_row = db.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
        address_id = address_id_row[0]
        print(f"Address created with ID: {address_id}")

        # 4. Insert User
        print("Hashing password and inserting User...")
        hashed_password = generate_password_hash(password)

        sql_insert_user = text("""
            INSERT INTO `User` (uname, uemail, upno, equity_funds, commodity_funds, address_id, password)
            VALUES (:uname, :uemail, :upno, 0.00, 0.00, :address_id, :password)
        """)
        
        db.session.execute(sql_insert_user, {
            'uname': uname,
            'uemail': uemail,
            'upno': data.get('upno', ''), 
            'address_id': address_id, 
            'password': hashed_password
        })
        
        # 5. Commit Transaction
        # This will trigger the SQL Trigger 'insert_portfolio_after_user'
        db.session.commit()
        print("--- REGISTRATION SUCCESSFUL ---")

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        db.session.rollback() # Undo changes if anything failed
        print("!!! ERROR DURING REGISTRATION !!!")
        print(traceback.format_exc()) # This prints the EXACT error to your console/docker logs
        return jsonify({"error": str(e)}), 500


# Route to log in a user
@user_bp.route('/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()

        # Validate that required fields are present
        uemail = data.get('uemail')
        password = data.get('password')

        if uemail is None or password is None:
            return jsonify({"error": "Email and password are required"}), 400

        # Retrieve the user record based on email
        sql_query = text("SELECT uid, uname, uemail, upno, equity_funds, commodity_funds, password FROM `User` WHERE uemail = :uemail LIMIT 1")
        user = db.session.execute(sql_query, {'uemail': uemail}).fetchone()

        # Check if user exists and password is valid
        if not user:
            return jsonify({"error": "User not found"}), 404

        if not check_password_hash(user[6], password):  # Password is at index 6 in the SELECT query
            return jsonify({"error": "Invalid credentials"}), 401

        # Create the response with user details (excluding password)
        user_data = {
            'uid': user[0],
            'uname': user[1],
            'uemail': user[2],
            'upno': user[3],
            'equity_funds': user[4],
            'commodity_funds': user[5]
        }

        return jsonify({"message": "Login successful", "user": user_data}), 200

    except KeyError as e:
        print(f"KeyError: {str(e)}")
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400

    except Exception as e:
        print(f"Error occurred during login: {str(e)}")
        return jsonify({"error": str(e)}), 500


@user_bp.route('/user/<int:uid>', methods=['GET'])
def get_user(uid):
    try:
        sql_query = text("""
            SELECT uid, uname, uemail, upno, equity_funds, commodity_funds, address_id
            FROM `User`
            WHERE uid = :uid
            LIMIT 1
        """)
        user = db.session.execute(sql_query, {'uid': uid}).fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_data = {
            'uid': user[0],
            'uname': user[1],
            'uemail': user[2],
            'upno': user[3],
            'equity_funds': user[4],
            'commodity_funds': user[5],
            'address_id': user[6]
        }

        return jsonify(user_data), 200
    except Exception as e:
        print(f"Error occurred fetching user details: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Route to update user details by UID
@user_bp.route('/user/<int:uid>', methods=['PUT'])
def update_user(uid):
    try:
        data = request.get_json()

        # Check if user exists
        user_exist = db.session.execute(text("SELECT uid FROM `User` WHERE uid = :uid"), {'uid': uid}).fetchone()
        if not user_exist:
            return jsonify({"error": "User not found"}), 404

        # Update fields, with password hashing if included
        fields = {key: data[key] for key in data if data[key] is not None}
        if 'password' in fields:
            fields['password'] = generate_password_hash(fields['password'])  # Hash the password if updating

        # Dynamic SQL query for update
        sql_query = text("""
            UPDATE `User`
            SET uname = :uname, uemail = :uemail, upno = :upno, 
                equity_funds = :equity_funds, commodity_funds = :commodity_funds, 
                address_id = :address_id, password = COALESCE(:password, password)
            WHERE uid = :uid
        """)
        
        db.session.execute(sql_query, {
            'uname': fields.get('uname'),
            'uemail': fields.get('uemail'),
            'upno': fields.get('upno'),
            'equity_funds': fields.get('equity_funds'),
            'commodity_funds': fields.get('commodity_funds'),
            'address_id': fields.get('address_id'),
            'password': fields.get('password'),
            'uid': uid
        })
        db.session.commit()

        return jsonify({"message": "User updated successfully"}), 200

    except Exception as e:
        print(f"Error updating user: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Route to delete a user by UID
@user_bp.route('/user/<int:uid>', methods=['DELETE'])
def delete_user(uid):
    try:
        user_exist = db.session.execute(text("SELECT uid FROM `User` WHERE uid = :uid"), {'uid': uid}).fetchone()
        if not user_exist:
            return jsonify({"error": "User not found"}), 404

        db.session.execute(text("DELETE FROM `User` WHERE uid = :uid"), {'uid': uid})
        db.session.commit()

        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting user: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@user_bp.route('/user/<int:uid>/password', methods=['PUT'])
def update_password(uid):
    try:
        data = request.get_json()

        current_password = data.get('current_password')
        new_password = data.get('new_password')

        if not current_password or not new_password:
            return jsonify({"error": "Current password and new password are required"}), 400

        # Retrieve current password hash for the user
        sql_query = text("""
            SELECT password FROM `User` WHERE uid = :uid
        """)
        result = db.session.execute(sql_query, {'uid': uid}).fetchone()

        if not result:
            return jsonify({"error": "User not found"}), 404

        stored_password_hash = result[0]

        # Verify current password
        if not check_password_hash(stored_password_hash, current_password):
            return jsonify({"error": "Current password is incorrect"}), 401

        # Hash the new password
        hashed_new_password = generate_password_hash(new_password)

        # Update password in the database
        update_query = text("""
            UPDATE `User` SET password = :new_password WHERE uid = :uid
        """)
        db.session.execute(update_query, {'new_password': hashed_new_password, 'uid': uid})
        db.session.commit()

        return jsonify({"message": "Password updated successfully"}), 200

    except Exception as e:
        print(f"Error updating password for user {uid}: {e}")
        return jsonify({"error": str(e)}), 500

@user_bp.route('/api/user/<int:uid>/funds_status', methods=['GET'])
def get_funds_status(uid):
    try:
        # Call the GetTotalPendingCostEquity function to get total pending cost for equity orders
        result_equity = db.session.execute(text(""" 
            SELECT GetTotalPendingCostEquity(:uid) AS total_pending_cost_equity; 
        """), {'uid': uid})

        # Call the GetTotalPendingCostCommodity function to get total pending cost for commodity orders
        result_commodity = db.session.execute(text(""" 
            SELECT GetTotalPendingCostCommodity(:uid) AS total_pending_cost_commodity; 
        """), {'uid': uid})

        # Call the GetTotalCostEquity function to get total cost for equity orders
        result_total_cost_equity = db.session.execute(text(""" 
            SELECT GetTotalCostEquity(:uid) AS total_cost_equity; 
        """), {'uid': uid})

        # Call the GetTotalCostCommodity function to get total cost for commodity orders
        result_total_cost_commodity = db.session.execute(text(""" 
            SELECT GetTotalCostCommodity(:uid) AS total_cost_commodity; 
        """), {'uid': uid})

        # Retrieve the results from each query
        total_pending_cost_equity = result_equity.fetchone()[0]
        total_pending_cost_commodity = result_commodity.fetchone()[0]
        total_cost_equity = result_total_cost_equity.fetchone()[0]
        total_cost_commodity = result_total_cost_commodity.fetchone()[0]

        # Fetch the equity funds available for the user
        result_equity_funds = db.session.execute(text("""
            SELECT equity_funds FROM `User` WHERE uid = :uid
        """), {'uid': uid})
        equity_funds = result_equity_funds.fetchone()[0]

        # Fetch the commodity funds available for the user
        result_commodity_funds = db.session.execute(text("""
            SELECT commodity_funds FROM `User` WHERE uid = :uid
        """), {'uid': uid})
        commodity_funds = result_commodity_funds.fetchone()[0]

        # Calculate available margin for equity and commodity
        available_margin_equity = 100000 + equity_funds - total_pending_cost_equity
        available_margin_commodity = 100000 + commodity_funds - total_pending_cost_commodity

        # Calculate utilized margin (total cost)
        utilized_margin_equity = total_cost_equity
        utilized_margin_commodity = total_cost_commodity

        # Return JSON response with all values
        return jsonify({
            'available_margin_equity': float(available_margin_equity),
            'available_margin_commodity': float(available_margin_commodity),
            'total_pending_cost_equity': float(total_pending_cost_equity),
            'total_pending_cost_commodity': float(total_pending_cost_commodity),
            'utilized_margin_equity': float(utilized_margin_equity),
            'utilized_margin_commodity': float(utilized_margin_commodity)
        })

    except Exception as e:
        print(f"Error fetching funds status: {e}")
        return jsonify({'error': 'Failed to fetch funds status'}), 500




### ADDRESS MANAGEMENT ###

# Get all addresses for a user
@user_bp.route('/user/<int:uid>/addresses', methods=['GET'])
def get_addresses(uid):
    try:
        sql_query = text("""
            SELECT a.address_id, a.locality, a.city, a.building, a.hno
            FROM Address a
            JOIN `User` u ON a.address_id = u.address_id
            WHERE u.uid = :uid
        """)
        addresses = db.session.execute(sql_query, {'uid': uid}).fetchall()

        if not addresses:
            return jsonify({"message": "No addresses found"}), 404

        return jsonify([
            {
                'address_id': row.address_id,
                'locality': row.locality,
                'city': row.city,
                'building': row.building,
                'hno': row.hno
            }
            for row in addresses
        ]), 200
    except Exception as e:
        print(f"Error fetching addresses: {e}")
        return jsonify({"error": "Failed to fetch addresses"}), 500


@user_bp.route('/user/<int:uid>/addresses', methods=['POST'])
def add_address(uid):
    try:
        # Parse the JSON body for address details
        data = request.get_json()
        hno = data.get('hno')
        locality = data.get('locality')
        city = data.get('city')
        building = data.get('building')

        # Validate input
        if not all([hno, locality, city, building]):
            return jsonify({"error": "All fields (hno, locality, city, building) are required"}), 400

        # Insert the new address into the Address table
        insert_address_query = text("""
            INSERT INTO Address (hno, locality, city, building)
            VALUES (:hno, :locality, :city, :building)
        """)
        db.session.execute(insert_address_query, {
            'hno': hno,
            'locality': locality,
            'city': city,
            'building': building
        })

        # Get the last inserted address ID
        last_address_id = db.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]

        # Commit the transaction
        db.session.commit()

        # Return the newly added address
        return jsonify({
            "address_id": last_address_id,
            "hno": hno,
            "locality": locality,
            "city": city,
            "building": building
        }), 201

    except Exception as e:
        print(f"Error adding address for user {uid}: {e}")
        return jsonify({"error": str(e)}), 500


@user_bp.route('/user/<int:uid>/addresses/<int:address_id>', methods=['DELETE'])
def delete_address(uid, address_id):
    try:
        # Check if the address exists and belongs to the user
        address_check_query = text("""
            SELECT address_id
            FROM Address
            WHERE address_id = :address_id
        """)
        address = db.session.execute(address_check_query, {'address_id': address_id}).fetchone()

        if not address:
            return jsonify({"error": "Address not found"}), 404

        # Remove the address if it's associated with the user
        delete_address_query = text("""
            DELETE FROM Address
            WHERE address_id = :address_id
        """)
        db.session.execute(delete_address_query, {'address_id': address_id})
        db.session.commit()

        return jsonify({"message": "Address deleted successfully"}), 200

    except Exception as e:
        print(f"Error deleting address {address_id} for user {uid}: {e}")
        return jsonify({"error": str(e)}), 500


# Add or withdraw funds
@user_bp.route('/user/<int:uid>/funds', methods=['POST'])
def manage_funds(uid):
    """
    Endpoint to add or withdraw funds for a user.
    """
    try:
        data = request.get_json()
        sql_query = ""
        # Validate input data
        fund_type = data.get('type')  # "equity" or "commodity"
        action = data.get('action')  # "add" or "withdraw"
        amount = float(data.get('amount', 0))  # Ensure amount is a number
        payment_mode = data.get('payment_mode')  # Dummy payment mode: "UPI" or "Card"

        if not fund_type or not action or amount <= 0:
            return jsonify({"error": "Invalid input"}), 400

        if fund_type not in ['equity', 'commodity'] or action not in ['add', 'withdraw']:
            return jsonify({"error": "Invalid fund type or action"}), 400

        # Determine the column to update based on fund type
        column = 'equity_funds' if fund_type == 'equity' else 'commodity_funds'

        # Determine the SQL operation
        if action == 'add':
            sql_query = text(f"UPDATE `User` SET {column} = {column} + :amount WHERE uid = :uid")
        elif action == 'withdraw':
            sql_query = text(f"""
                UPDATE `User`
                SET {column} = CASE
                    WHEN {column} >= :amount THEN {column} - :amount
                    ELSE {column} -- Prevent negative funds
                END
                WHERE uid = :uid
            """)

        # Execute the query
        result = db.session.execute(sql_query, {'amount': amount, 'uid': uid})
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({"error": "User not found or insufficient funds"}), 400

        # Fetch updated funds
        user_query = text(f"SELECT equity_funds, commodity_funds FROM `User` WHERE uid = :uid")
        user = db.session.execute(user_query, {'uid': uid}).fetchone()

        return jsonify({
            "message": f"Funds {action}ed successfully",
            "equity_funds": float(user[0]),
            "commodity_funds": float(user[1]),
        }), 200

    except Exception as e:
        print(f"Error managing funds for user {uid}: {e}")
        return jsonify({"error": "Failed to manage funds"}), 500