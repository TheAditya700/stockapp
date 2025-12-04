from extensions import db
from sqlalchemy.dialects.mysql import ENUM, DECIMAL

# 1. Address Model
class Address(db.Model):
    __tablename__ = 'Address'
    address_id = db.Column(db.Integer, primary_key=True)
    locality = db.Column(db.String(100))
    city = db.Column(db.String(100))
    building = db.Column(db.String(100))
    hno = db.Column(db.String(20))

    # Relationships
    user = db.relationship('User', back_populates='address', uselist=False)

# 2. User Model
class User(db.Model):
    __tablename__ = 'User'
    uid = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(100), nullable=False)
    uemail = db.Column(db.String(100), unique=True, nullable=False)
    upno = db.Column(db.String(20))
    # Use Numeric for money to match DECIMAL(15, 2) in SQL
    equity_funds = db.Column(db.Numeric(15, 2), default=0.00)
    commodity_funds = db.Column(db.Numeric(15, 2), default=0.00)
    address_id = db.Column(db.Integer, db.ForeignKey('Address.address_id'))
    password = db.Column(db.String(255), nullable=False)

    # Relationships
    address = db.relationship('Address', back_populates='user')
    nominees = db.relationship('Nominee', back_populates='user', cascade='all, delete')
    # Use string reference for Portfolio to avoid circular import issues if they arise
    portfolios = db.relationship('Portfolio', back_populates='user', cascade='all, delete')
    watchlists = db.relationship('Watchlist', back_populates='user', cascade='all, delete')
    orders = db.relationship('Orders', back_populates='user', cascade='all, delete')

# 3. Asset Model
class Asset(db.Model):
    __tablename__ = 'Asset'
    aid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Added asset_type to match SQL
    asset_type = db.Column(ENUM('Equity', 'Commodity'), nullable=False, default='Equity')

    # Relationships
    prices = db.relationship('Price', back_populates='asset', cascade='all, delete')
    portfolio_assets = db.relationship('Portfolio_Asset', back_populates='asset', cascade='all, delete')
    orders = db.relationship('Orders', back_populates='asset')

# 4. Price Model (Historical Data)
class Price(db.Model):
    __tablename__ = 'Price'
    aid = db.Column(db.Integer, db.ForeignKey('Asset.aid'), primary_key=True)
    date = db.Column(db.Date, primary_key=True)
    open_price = db.Column(db.Numeric(10, 2))
    close_price = db.Column(db.Numeric(10, 2))
    high = db.Column(db.Numeric(10, 2))
    low = db.Column(db.Numeric(10, 2))
    volume = db.Column(db.BigInteger)

    # Relationships
    asset = db.relationship('Asset', back_populates='prices')

# 5. Orders Model
class Orders(db.Model):
    __tablename__ = 'Orders'
    oid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('User.uid'))
    aid = db.Column(db.Integer, db.ForeignKey('Asset.aid'))  # Added Link to Asset
    price = db.Column(db.Numeric(10, 2))
    qty = db.Column(db.Integer)
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    otype = db.Column(db.String(50))  # Buy or Sell
    status = db.Column(db.String(20), default='Pending')

    # Relationships
    user = db.relationship('User', back_populates='orders')
    asset = db.relationship('Asset', back_populates='orders')

# 6. Transaction Model (Updated for Matching Engine)
class Transaction(db.Model):
    __tablename__ = 'Transaction'
    tid = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    buy_oid = db.Column(db.Integer, db.ForeignKey('Orders.oid'))
    sell_oid = db.Column(db.Integer, db.ForeignKey('Orders.oid'))
    buy_uid = db.Column(db.Integer, db.ForeignKey('User.uid'))
    sell_uid = db.Column(db.Integer, db.ForeignKey('User.uid'))
    price = db.Column(db.Numeric(10, 2))
    qty = db.Column(db.Integer)

    # Relationships
    buy_order = db.relationship('Orders', foreign_keys=[buy_oid])
    sell_order = db.relationship('Orders', foreign_keys=[sell_oid])
    buyer = db.relationship('User', foreign_keys=[buy_uid])
    seller = db.relationship('User', foreign_keys=[sell_uid])

# 7. Portfolio Model
class Portfolio(db.Model):
    __tablename__ = 'Portfolio'
    pid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('User.uid'))
    pname = db.Column(db.String(100))

    # Relationships
    user = db.relationship('User', back_populates='portfolios')
    # Relationship to the association table
    portfolio_assets = db.relationship('Portfolio_Asset', back_populates='portfolio', cascade='all, delete')

# 8. Portfolio_Asset (Association Object with Data)
class Portfolio_Asset(db.Model):
    __tablename__ = 'Portfolio_Asset'
    pid = db.Column(db.Integer, db.ForeignKey('Portfolio.pid'), primary_key=True)
    aid = db.Column(db.Integer, db.ForeignKey('Asset.aid'), primary_key=True)
    qty = db.Column(db.Integer, default=0)
    buy_price = db.Column(db.Numeric(10, 2), default=0.00)

    # Relationships
    portfolio = db.relationship('Portfolio', back_populates='portfolio_assets')
    asset = db.relationship('Asset', back_populates='portfolio_assets')

# 9. Watchlist Model
class Watchlist(db.Model):
    __tablename__ = 'Watchlist'
    wid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('User.uid'))
    wname = db.Column(db.String(100))

    # Relationships
    user = db.relationship('User', back_populates='watchlists')
    watchlist_assets = db.relationship('Watchlist_Asset', back_populates='watchlist', cascade='all, delete')

# 10. Watchlist_Asset (Simple Many-to-Many)
class Watchlist_Asset(db.Model):
    __tablename__ = 'Watchlist_Asset'
    wid = db.Column(db.Integer, db.ForeignKey('Watchlist.wid'), primary_key=True)
    aid = db.Column(db.Integer, db.ForeignKey('Asset.aid'), primary_key=True)

    # Relationships
    watchlist = db.relationship('Watchlist', back_populates='watchlist_assets')
    asset = db.relationship('Asset', back_populates='watchlist_assets')

# 11. Nominee Model
class Nominee(db.Model):
    __tablename__ = 'Nominee'
    uid = db.Column(db.Integer, db.ForeignKey('User.uid'), primary_key=True)
    nid = db.Column(db.Integer, primary_key=True)
    nemail = db.Column(db.String(100))
    ntype = db.Column(db.String(50))
    relation = db.Column(db.String(50))
    nname = db.Column(db.String(100))

    # Relationships
    user = db.relationship('User', back_populates='nominees')