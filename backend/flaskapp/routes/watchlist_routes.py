from flask import Blueprint, jsonify, request
from sqlalchemy import text
from models import db

# Blueprint setup for asset-related routes
watchlist_bp = Blueprint('watchlist', __name__)

# Fetch all watchlists for a specific user
@watchlist_bp.route('/watchlists/<int:uid>', methods=['GET'])
def get_watchlists(uid):
    try:
        sql_query = text("""
            SELECT wid, wname 
            FROM Watchlist
            WHERE uid = :uid
        """)
        result = db.session.execute(sql_query, {'uid': uid})
        watchlists = result.fetchall()

        if not watchlists:
            return jsonify([])

        return jsonify([{'wid': row.wid, 'wname': row.wname} for row in watchlists])

    except Exception as e:
        print(f"Error fetching watchlists for user {uid}: {e}")
        return jsonify({'error': 'An error occurred while fetching watchlists'}), 500


# Fetch assets in a specific watchlist
@watchlist_bp.route('/watchlists/<int:wid>/assets', methods=['GET'])
def get_watchlist_assets(wid):
    try:
        sql_query = text("""
            SELECT a.aid, a.name, apv.current_price
            FROM Watchlist_Asset wa
            JOIN Asset a ON wa.aid = a.aid
            JOIN AssetPriceView apv ON wa.aid = apv.aid
            WHERE wa.wid = :wid
        """)
        result = db.session.execute(sql_query, {'wid': wid})
        assets = result.fetchall()

        if not assets:
            return jsonify([])

        return jsonify([
            {'aid': row.aid, 'name': row.name, 'current_price': row.current_price}
            for row in assets
        ])

    except Exception as e:
        print(f"Error fetching assets for watchlist {wid}: {e}")
        return jsonify({'error': 'An error occurred while fetching watchlist assets'}), 500


# Add a new watchlist for a specific user
@watchlist_bp.route('/watchlists', methods=['POST'])
def add_watchlist():
    try:
        data = request.get_json()
        uid = data.get('uid')
        wname = data.get('name')

        if not uid or not wname:
            return jsonify({'error': 'Missing required fields (uid, name).'}), 400

        sql_query = text("""
            INSERT INTO Watchlist (wname, uid) 
            VALUES (:wname, :uid)
        """)
        db.session.execute(sql_query, {'wname': wname, 'uid': uid})
        db.session.commit()

        return jsonify({'message': 'Watchlist created successfully'}), 201

    except Exception as e:
        print(f"Error adding watchlist: {e}")
        return jsonify({'error': 'An error occurred while adding the watchlist'}), 500


# Add an asset to the watchlist
@watchlist_bp.route('/watchlists/<int:wid>/assets', methods=['POST'])
def add_asset_to_watchlist(wid):
    try:
        data = request.get_json()
        aid = data.get('aid')

        if not aid:
            return jsonify({'error': 'Missing required field (aid).'}), 400

        sql_query_check = text("""
            SELECT * 
            FROM Watchlist_Asset 
            WHERE wid = :wid AND aid = :aid
        """)
        existing_entry = db.session.execute(sql_query_check, {'wid': wid, 'aid': aid}).fetchone()

        if not existing_entry:
            sql_query_insert = text("""
                INSERT INTO Watchlist_Asset (wid, aid) 
                VALUES (:wid, :aid)
            """)
            db.session.execute(sql_query_insert, {'wid': wid, 'aid': aid})
            db.session.commit()

        return jsonify({'message': 'Asset added to watchlist successfully'})

    except Exception as e:
        print(f"Error adding asset {aid} to watchlist {wid}: {e}")
        return jsonify({'error': 'An error occurred while adding asset to watchlist'}), 500


# Remove an asset from the watchlist
@watchlist_bp.route('/watchlists/<int:wid>/assets/<int:aid>', methods=['DELETE'])
def remove_asset_from_watchlist(wid, aid):
    try:
        sql_query_delete = text("""
            DELETE FROM Watchlist_Asset 
            WHERE wid = :wid AND aid = :aid
        """)
        result = db.session.execute(sql_query_delete, {'wid': wid, 'aid': aid})
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({'error': 'Asset not found in watchlist'}), 404

        return jsonify({'message': 'Asset removed from watchlist successfully'}), 200

    except Exception as e:
        print(f"Error removing asset {aid} from watchlist {wid}: {e}")
        return jsonify({'error': 'An error occurred while removing asset from watchlist'}), 500


# Delete an entire watchlist
@watchlist_bp.route('/watchlists/<int:wid>', methods=['DELETE'])
def delete_watchlist(wid):
    try:
        # Remove dependent assets first
        db.session.execute(text("""
            DELETE FROM Watchlist_Asset 
            WHERE wid = :wid
        """), {'wid': wid})

        # Delete the watchlist itself
        result = db.session.execute(text("""
            DELETE FROM Watchlist 
            WHERE wid = :wid
        """), {'wid': wid})
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({'error': 'Watchlist not found'}), 404

        return jsonify({'message': 'Watchlist deleted successfully'}), 200

    except Exception as e:
        print(f"Error deleting watchlist {wid}: {e}")
        return jsonify({'error': 'An error occurred while deleting the watchlist'}), 500
