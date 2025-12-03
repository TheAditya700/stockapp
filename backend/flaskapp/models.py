from extensions import db

# User Model
class User(db.Model):
    __tablename__ = 'User'
    uid = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(100), nullable=False)
    uemail = db.Column(db.String(100), unique=True, nullable=False)
    upno = db.Column(db.String(20))
    equity_funds = db.Column(db.Float, default=0.00)
    commodity_funds = db.Column(db.Float, default=0.00)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'))
    password = db.Column(db.String(128), nullable=False)  # Plain password field without hashing

    
    # Relationships
    address = db.relationship('Address', back_populates='user')
    nominees = db.relationship('Nominee', back_populates='user', cascade='all, delete')
    portfolios = db.relationship('Portfolio', back_populates='user', cascade='all, delete')
    watchlists = db.relationship('Watchlist', back_populates='user', cascade='all, delete')
    orders = db.relationship('Orders', back_populates='user', cascade='all, delete')

# Address Model
class Address(db.Model):
    __tablename__ = 'Address'
    address_id = db.Column(db.Integer, primary_key=True)
    locality = db.Column(db.String(100))
    city = db.Column(db.String(100))
    building = db.Column(db.String(100))
    hno = db.Column(db.String(20))

    # Relationships
    user = db.relationship('User', back_populates='address')

# Nominee Model
class Nominee(db.Model):
    __tablename__ = 'nominee'
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'), primary_key=True)
    nid = db.Column(db.Integer, primary_key=True)
    nemail = db.Column(db.String(100))
    ntype = db.Column(db.String(50))
    relation = db.Column(db.String(50))
    nname = db.Column(db.String(100))

    # Relationships
    user = db.relationship('User', back_populates='nominees')

# Orders Model
class Orders(db.Model):
    __tablename__ = 'Orders'
    oid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)
    date = db.Column(db.Date)
    otype = db.Column(db.String(50))  # Buy or Sell
    status = db.Column(db.String(20), default='Pending')
    time = db.Column(db.Time)

    # Relationships
    user = db.relationship('User', back_populates='orders')
    transaction = db.relationship('Transaction', back_populates='order', cascade='all, delete')

# Transaction Model
class Transaction(db.Model):
    __tablename__ = 'Transaction'
    tid = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    status = db.Column(db.String(50))
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'))
    oid = db.Column(db.Integer, db.ForeignKey('orders.oid'))

    # Relationships
    order = db.relationship('Orders', back_populates='transaction')
    transaction_assets = db.relationship('Transaction_Asset', back_populates='transaction', cascade='all, delete')

# Portfolio Model
class Portfolio(db.Model):
    __tablename__ = 'Portfolio'
    pid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'))
    pname = db.Column(db.String(100))
    total_val = db.Column(db.Float, default=0.00)

    # Relationships
    user = db.relationship('User', back_populates='portfolios')
    portfolio_assets = db.relationship('Portfolio_Asset', back_populates='portfolio', cascade='all, delete')

# Watchlist Model
class Watchlist(db.Model):
    __tablename__ = 'Watchlist'
    wid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'))
    wname = db.Column(db.String(100))
    total_val = db.Column(db.Float, default=0.00)

    # Relationships
    user = db.relationship('User', back_populates='watchlists')
    watchlist_assets = db.relationship('Watchlist_Asset', back_populates='watchlist', cascade='all, delete')

# Asset Model
class Asset(db.Model):
    __tablename__ = 'Asset'
    aid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

    # Relationships
    portfolio_assets = db.relationship('Portfolio_Asset', back_populates='asset', cascade='all, delete')
    watchlist_assets = db.relationship('Watchlist_Asset', back_populates='asset', cascade='all, delete')
    transaction_assets = db.relationship('Transaction_Asset', back_populates='asset', cascade='all, delete')

# Many-to-Many relationship between Portfolio and Asset
class Portfolio_Asset(db.Model):
    __tablename__ = 'Portfolio_Asset'
    pid = db.Column(db.Integer, db.ForeignKey('portfolio.pid'), primary_key=True)
    aid = db.Column(db.Integer, db.ForeignKey('asset.aid'), primary_key=True)

    # Relationships
    portfolio = db.relationship('Portfolio', back_populates='portfolio_assets')
    asset = db.relationship('Asset', back_populates='portfolio_assets')

# Many-to-Many relationship between Watchlist and Asset
class Watchlist_Asset(db.Model):
    __tablename__ = 'Watchlist_Asset'
    wid = db.Column(db.Integer, db.ForeignKey('watchlist.wid'), primary_key=True)
    aid = db.Column(db.Integer, db.ForeignKey('asset.aid'), primary_key=True)

    # Relationships
    watchlist = db.relationship('Watchlist', back_populates='watchlist_assets')
    asset = db.relationship('Asset', back_populates='watchlist_assets')

# Many-to-Many relationship between Transaction and Asset
class Transaction_Asset(db.Model):
    __tablename__ = 'Transaction_Asset'
    tid = db.Column(db.Integer, db.ForeignKey('transaction.tid'), primary_key=True)
    aid = db.Column(db.Integer, db.ForeignKey('asset.aid'), primary_key=True)
    qty = db.Column(db.Integer)

    # Relationships
    transaction = db.relationship('Transaction', back_populates='transaction_assets')
    asset = db.relationship('Asset', back_populates='transaction_assets')