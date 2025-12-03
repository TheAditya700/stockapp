from flask import Blueprint, jsonify, request
from sqlalchemy import text
from extensions import db
import logging

# Create the blueprint for orders-related routes
orders_bp = Blueprint('orders_bp', __name__)

# Define the API route to get orders for a specific user
@orders_bp.route('/orders/<int:uid>', methods=['GET'])
def get_orders(uid):
    # SQL query to fetch orders for the given user ID
    sql_query = text("""
        SELECT 
            o.oid, 
            o.otype, 
            o.qty, 
            o.price, 
            o.status, 
            o.date, 
            a.name AS asset_name 
        FROM 
            Orders o
        JOIN 
            Asset a ON o.aid = a.aid 
        WHERE 
            o.uid = :uid
        ORDER BY 
            o.date DESC;
    """)
    
    # Execute the query
    result = db.session.execute(sql_query, {'uid': uid})
    orders = result.fetchall()

    # Format the response as JSON
    orders_list = [
        {
            'oid': row.oid,
            'otype': row.otype,
            'qty': row.qty,
            'price': row.price,
            'status': row.status,
            'date': row.date.strftime('%Y-%m-%d'),
            'asset_name': row.asset_name
        }
        for row in orders
    ]
    
    return jsonify(orders_list)

# Define the API route to place an order
@orders_bp.route('/place_order', methods=['POST'])
def place_order():
    try:
        # Get JSON data from the request
        data = request.get_json()
        uid = data.get('uid')
        aid = data.get('aid')
        qty = data.get('qty')
        otype = data.get('otype')  # Order type is passed directly in the request

        # Validate request parameters
        if not uid or not aid or not qty or not otype:
            return jsonify({'error': 'Missing required fields (uid, aid, qty, otype).'}), 400

        # Prepare the call to the stored procedure
        sql_query = text("CALL place_order(:uid, :aid, :qty, :otype)")

        # Debugging: Print SQL query and parameters
        print("Executing SQL:", sql_query)
        print("With parameters:", {'uid': uid, 'aid': aid, 'qty': qty, 'otype': otype})
        
        # Execute the stored procedure with given parameters
        db.session.execute(sql_query, {
            'uid': uid,
            'aid': aid,
            'qty': qty,
            'otype': otype
        })

        sql_query_match_orders = text("CALL MatchOrders()")
        db.session.execute(sql_query_match_orders)
        
        # Commit the transaction
        db.session.commit()

        # Return a success response
        return jsonify({'message': 'Order placed successfully!'}), 200

    except Exception as e:
        # Check for margin-exceeded error based on SQLSTATE '45000' in MySQL
        if 'Order exceeds available margin' in str(e):
            logging.warning("Margin limit exceeded while placing order")
            return jsonify({'error': 'Order exceeds available margin'}), 400
        else:
            # Capture any other SQL or execution errors and log them
            logging.error(f"Error placing order: {str(e)}")
            print("Error occurred while placing order:", str(e))
            return jsonify({'error': f'Failed to place order: {str(e)}'}), 500



@orders_bp.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    try:
        # Check if the order exists and get its status
        order_query = text("SELECT status, uid, qty, aid, price FROM Orders WHERE oid = :order_id")
        order_result = db.session.execute(order_query, {'order_id': order_id}).fetchone()

        if not order_result:
            return jsonify({'error': 'Order not found'}), 404

        # Destructure the result
        status, uid, qty, aid, price = order_result

        # If the order is "Completed," skip fund adjustment and simply delete
        if status == "Completed":
            delete_query = text("DELETE FROM Orders WHERE oid = :order_id")
            db.session.execute(delete_query, {'order_id': order_id})
            db.session.commit()
            return jsonify({'message': 'Completed order deleted successfully'}), 200

        # For pending orders, adjust the user's funds and then delete
        # Determine the asset type and update funds accordingly
        asset_type_query = text("SELECT asset_type FROM Asset WHERE aid = :aid")
        asset_type = db.session.execute(asset_type_query, {'aid': aid}).scalar()

        if asset_type == "Equity":
            fund_update_query = text("UPDATE `User` SET equity_funds = equity_funds + :amount WHERE uid = :uid")
        elif asset_type == "Commodity":
            fund_update_query = text("UPDATE `User` SET commodity_funds = commodity_funds + :amount WHERE uid = :uid")
        else:
            raise ValueError("Invalid asset type")

        # Calculate the total amount for the funds adjustment
        amount = qty * price
        db.session.execute(fund_update_query, {'amount': amount, 'uid': uid})

        # Delete the order after updating funds
        delete_query = text("DELETE FROM Orders WHERE oid = :order_id")
        db.session.execute(delete_query, {'order_id': order_id})
        db.session.commit()

        return jsonify({'message': 'Order deleted successfully'}), 200

    except Exception as e:
        # Detailed logging of the exception for troubleshooting
        return jsonify({'error': f"Failed to delete order: {str(e)}"}), 500
