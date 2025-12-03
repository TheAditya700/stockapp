from flask import Blueprint, jsonify, request
from sqlalchemy import text
from extensions import db

portfolio_bp = Blueprint('portfolio_bp', __name__)

# API route to get a user's portfolio based on uid
@portfolio_bp.route('/portfolio/<int:uid>', methods=['GET'])
def get_portfolio(uid):
    # SQL query to fetch the user's portfolio with buy price, profit, and profit percentage
    sql_query = text("""
        SELECT 
            pa.pid, 
            p.pname, 
            a.name AS asset_name, 
            pa.qty, 
            pa.buy_price,
            apv.current_price, 
            (pa.qty * apv.current_price) AS total_value,
            (apv.current_price - pa.buy_price) AS profit, 
            ((apv.current_price - pa.buy_price) / pa.buy_price) * 100 AS profit_percentage
        FROM 
            Portfolio_Asset pa
        JOIN 
            Portfolio p ON pa.pid = p.pid
        JOIN 
            AssetPriceView apv ON pa.aid = apv.aid
        JOIN 
            Asset a ON pa.aid = a.aid
        WHERE 
            p.uid = :uid;
    """)

    # Execute the query
    result = db.session.execute(sql_query, {'uid': uid})
    portfolio_data = result.fetchall()

    # Format the result into a JSON-friendly format
    portfolio_list = [
        {
            'pid': row[0],
            'pname': row[1],
            'asset_name': row[2],
            'qty': row[3],
            'buy_price': row[4],
            'current_price': row[5],
            'total_value': row[6],
            'profit': row[7],
            'profit_percentage': row[8]
        }
        for row in portfolio_data
    ]

    # Return the portfolio data as JSON
    return jsonify(portfolio_list)

@portfolio_bp.route('/user/<int:uid>/portfolio_value', methods=['GET'])
def get_portfolio_value(uid):
    try:
        # Fetch the total portfolio value for the specified user
        sql_query = text("""
            SELECT total_value 
            FROM PortfolioTotalValueView 
            WHERE uid = :uid
        """)
        result = db.session.execute(sql_query, {'uid': uid})
        portfolio_value = result.fetchone()

        if portfolio_value:
            return jsonify({'total_portfolio_value': float(portfolio_value[0])}), 200
        else:
            return jsonify({'total_portfolio_value': 0.0}), 200

    except Exception as e:
        print(f"Error fetching portfolio value: {e}")
        return jsonify({'error': 'Failed to fetch portfolio value'}), 500

# API route to get a user's total portfolio profit and profit percentage based on uid
@portfolio_bp.route('/portfolio/summary/<int:uid>', methods=['GET'])
def get_portfolio_summary(uid):
    # SQL query to calculate total profit and total profit percentage for the user's portfolio
    sql_query = text("""
        SELECT 
            SUM((apv.current_price - pa.buy_price) * pa.qty) AS total_profit,
            CASE 
                WHEN SUM(pa.buy_price * pa.qty) = 0 THEN 0
                ELSE (SUM((apv.current_price - pa.buy_price) * pa.qty) / SUM(pa.buy_price * pa.qty)) * 100 
            END AS total_profit_percentage
        FROM 
            Portfolio_Asset pa
        JOIN 
            Portfolio p ON pa.pid = p.pid
        JOIN 
            AssetPriceView apv ON pa.aid = apv.aid
        WHERE 
            p.uid = :uid;
    """)

    # Execute the query
    result = db.session.execute(sql_query, {'uid': uid})
    summary_data = result.fetchone()

    # Format the response as JSON
    summary = {
        'total_profit': float(summary_data.total_profit) if summary_data.total_profit is not None else 0,
        'total_profit_percentage': float(summary_data.total_profit_percentage) if summary_data.total_profit_percentage is not None else 0
    }

    return jsonify(summary)

@portfolio_bp.route('/user/<int:uid>/total_values', methods=['GET'])
def get_total_values(uid):
    try:
        # SQL query to calculate the total value of equity and commodity in the portfolio
        sql_query = text("""
            SELECT
                SUM(CASE WHEN a.asset_type = 'Equity' THEN (pa.qty * apv.current_price) ELSE 0 END) AS total_equity_value,
                SUM(CASE WHEN a.asset_type = 'Commodity' THEN (pa.qty * apv.current_price) ELSE 0 END) AS total_commodity_value
            FROM
                Portfolio_Asset pa
            JOIN
                Portfolio p ON pa.pid = p.pid
            JOIN
                Asset a ON pa.aid = a.aid
            JOIN
                AssetPriceView apv ON pa.aid = apv.aid
            WHERE
                p.uid = :uid
        """)

        # Execute the query
        result = db.session.execute(sql_query, {'uid': uid})
        total_values = result.fetchone()

        # If no data is found, set default values to 0.0
        total_equity_value = float(total_values[0]) if total_values[0] is not None else 0.0
        total_commodity_value = float(total_values[1]) if total_values[1] is not None else 0.0

        # Return the result as JSON
        return jsonify({
            'total_equity_value': total_equity_value,
            'total_commodity_value': total_commodity_value
        })

    except Exception as e:
        print(f"Error fetching total values: {e}")
        return jsonify({'error': 'Failed to fetch total equity and commodity values'}), 500
