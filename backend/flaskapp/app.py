from flask import Flask
from flask_restful import Api
from extensions import db  # Import db from extensions
from routes.asset_routes import asset_bp  # Import the blueprint
from routes.portfolio_routes import portfolio_bp
from routes.orders_routes import orders_bp
from routes.watchlist_routes import watchlist_bp
from routes.user_routes import user_bp
from flask_cors import CORS  # Import Flask-CORS
from flask_login import LoginManager

# Initialize Flask
app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'

CORS(app)


# Configure the MySQL connection (adjust to your setup)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:linux@localhost/stock_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)  # Use db.init_app() to bind db to Flask app
api = Api(app)

# Initialize LoginManager and link it to the app
login_manager = LoginManager()
login_manager.init_app(app)  # This binds the LoginManager to your Flask app

login_manager.login_view = 'auth_bp.login'  # Set the login view for unauthorized access

# Register the blueprint for API routes
app.register_blueprint(asset_bp, url_prefix='/api')
app.register_blueprint(portfolio_bp, url_prefix='/api')
app.register_blueprint(orders_bp, url_prefix='/api')
app.register_blueprint(watchlist_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/')

# Error handling for database connection issues
@app.errorhandler(Exception)
def handle_error(e):
    return {'error': str(e)}, 500

# Create the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
