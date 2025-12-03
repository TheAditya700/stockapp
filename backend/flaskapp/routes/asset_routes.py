from flask import Blueprint, jsonify, request
from extensions import db  # Import db from extensions
from sqlalchemy import text

# Define the blueprint
asset_bp = Blueprint('asset_bp', __name__)

# Define a route within the blueprint
@asset_bp.route('/assets/search', methods=['GET'])
def search_assets():
    try:
        query = request.args.get('q', '')

        # If the query is empty, fetch all assets or limit it for performance
        if not query:
            sql_query = text("SELECT aid, name, current_price FROM AssetPriceView LIMIT 50")
            result = db.session.execute(sql_query)
        else:
            # Raw SQL query using AssetPriceView with a LIKE clause for search
            sql_query = text("SELECT aid, name, current_price FROM AssetPriceView WHERE name LIKE :query")
            result = db.session.execute(sql_query, {'query': f'%{query}%'})

        # Fetch results and construct the response
        assets = result.fetchall()
        assets_list = [{'aid': row[0], 'name': row[1], 'price': row[2]} for row in assets]

        return jsonify(assets_list)

    except Exception as e:
        # Log the error and return a generic message
        print(f"Error occurred while searching for assets: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching assets.'}), 500

# Route to get details of a single asset by aid
@asset_bp.route('/assets/<int:aid>', methods=['GET'])
def get_asset(aid):
    try:
        # SQL query to fetch a single asset's details
        sql_query = text("SELECT aid, name, current_price FROM AssetPriceView WHERE aid = :aid")
        result = db.session.execute(sql_query, {'aid': aid})
        asset = result.fetchone()

        if asset:
            asset_data = {'aid': asset[0], 'name': asset[1], 'price': asset[2]}
            return jsonify(asset_data), 200
        else:
            return jsonify({'error': 'Asset not found'}), 404

    except Exception as e:
        print(f"Error occurred while fetching asset: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching the asset.'}), 500

# Route to get historical prices of an asset
@asset_bp.route('/assets/prices/<int:aid>', methods=['GET'])
def get_asset_prices(aid):
    try:
        sql_query = text("""
            SELECT date, close_price
            FROM Price
            WHERE aid = :aid
            ORDER BY date ASC
        """)
        result = db.session.execute(sql_query, {'aid': aid})
        prices = result.fetchall()

        # Convert SQLAlchemy result to JSON serializable format
        price_data = [
            {
                'date': row.date.strftime('%Y-%m-%d'),
                'close_price': float(row.close_price)
            }
            for row in prices
        ]
        return jsonify(price_data), 200

    except Exception as e:
        print(f"Error fetching asset prices: {e}")
        return jsonify({'error': 'Failed to fetch asset prices'}), 500
