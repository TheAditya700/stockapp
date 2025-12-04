DROP DATABASE IF EXISTS stock_app;
CREATE DATABASE stock_app;
USE stock_app;

-- 1. Address Table
CREATE TABLE Address (
    address_id INT AUTO_INCREMENT PRIMARY KEY,
    locality VARCHAR(100),
    city VARCHAR(100),
    building VARCHAR(100),
    hno VARCHAR(20)
);

-- 2. User Table (Added password)
CREATE TABLE User (
    uid INT AUTO_INCREMENT PRIMARY KEY,
    uname VARCHAR(100) NOT NULL,
    uemail VARCHAR(100) UNIQUE NOT NULL,
    upno VARCHAR(20),
    equity_funds DECIMAL(15, 2) DEFAULT 0.00,
    commodity_funds DECIMAL(15, 2) DEFAULT 0.00,
    address_id INT,
    password VARCHAR(255), 
    CONSTRAINT fk_user_address FOREIGN KEY (address_id) REFERENCES Address(address_id)
);

-- 3. Asset Table (Added asset_type)
CREATE TABLE Asset (
    aid INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    asset_type ENUM('Equity', 'Commodity') NOT NULL DEFAULT 'Equity'
);

-- 4. Price Table
CREATE TABLE Price (
    aid INT,
    date DATETIME,
    open_price DECIMAL(10, 2),
    close_price DECIMAL(10, 2),
    high DECIMAL(10, 2),
    low DECIMAL(10, 2),
    volume BIGINT,
    PRIMARY KEY (aid, date),
    CONSTRAINT fk_price_asset FOREIGN KEY (aid) REFERENCES Asset(aid)
);

-- 5. AssetPriceView (Needed for Procedures)
CREATE OR REPLACE VIEW AssetPriceView AS
SELECT 
    a.aid, 
    a.name, 
    a.asset_type,
    p.close_price AS current_price
FROM 
    Asset a
JOIN 
    Price p ON a.aid = p.aid
JOIN 
    (SELECT aid, MAX(date) AS latest_date FROM Price GROUP BY aid) AS latest_prices
        ON p.aid = latest_prices.aid AND p.date = latest_prices.latest_date;

-- 6. Orders Table (Added aid)
CREATE TABLE Orders (
    oid INT AUTO_INCREMENT PRIMARY KEY,
    uid INT,
    aid INT,
    price DECIMAL(10, 2),
    qty INT,
    date DATE,
    time TIME,
    otype VARCHAR(50),
    status VARCHAR(20) DEFAULT 'Pending',
    CONSTRAINT fk_orders_user FOREIGN KEY (uid) REFERENCES User(uid),
    CONSTRAINT fk_orders_asset FOREIGN KEY (aid) REFERENCES Asset(aid)
);

-- 7. Transaction Table 
-- CRITICAL FIX: Updated columns to match your MatchOrders procedure
CREATE TABLE Transaction (
    tid INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    buy_oid INT,
    sell_oid INT,
    buy_uid INT,
    sell_uid INT,
    price DECIMAL(10, 2),
    qty INT,
    CONSTRAINT fk_trans_buy_order FOREIGN KEY (buy_oid) REFERENCES Orders(oid),
    CONSTRAINT fk_trans_sell_order FOREIGN KEY (sell_oid) REFERENCES Orders(oid),
    CONSTRAINT fk_trans_buy_user FOREIGN KEY (buy_uid) REFERENCES User(uid),
    CONSTRAINT fk_trans_sell_user FOREIGN KEY (sell_uid) REFERENCES User(uid)
);

-- 8. Portfolio Table
CREATE TABLE Portfolio (
    pid INT AUTO_INCREMENT PRIMARY KEY,
    uid INT,
    pname VARCHAR(100),
    CONSTRAINT fk_portfolio_user FOREIGN KEY (uid) REFERENCES User(uid)
);

-- 9. Portfolio_Asset Table (Added buy_price)
CREATE TABLE Portfolio_Asset (
    pid INT,
    aid INT,
    qty INT NOT NULL DEFAULT 0,
    buy_price DECIMAL(10, 2) DEFAULT 0.00,
    PRIMARY KEY (pid, aid),
    CONSTRAINT fk_portfolio_asset_portfolio FOREIGN KEY (pid) REFERENCES Portfolio(pid) ON DELETE CASCADE,
    CONSTRAINT fk_portfolio_asset_asset FOREIGN KEY (aid) REFERENCES Asset(aid)
);

-- 10. Watchlist Table
CREATE TABLE Watchlist (
    wid INT AUTO_INCREMENT PRIMARY KEY,
    uid INT,
    wname VARCHAR(100),
    CONSTRAINT fk_watchlist_user FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE
);

-- 11. Watchlist_Asset Table
CREATE TABLE Watchlist_Asset (
    wid INT,
    aid INT,
    PRIMARY KEY (wid, aid),
    CONSTRAINT fk_watchlist_asset_watchlist FOREIGN KEY (wid) REFERENCES Watchlist(wid) ON DELETE CASCADE,
    CONSTRAINT fk_watchlist_asset_asset FOREIGN KEY (aid) REFERENCES Asset(aid)
);

-- 12. PortfolioTotalValueView
CREATE OR REPLACE VIEW PortfolioTotalValueView AS
SELECT 
    p.pid, 
    p.uid, 
    p.pname, 
    SUM(pa.qty * apv.current_price) AS total_value
FROM 
    Portfolio p
JOIN 
    Portfolio_Asset pa ON p.pid = pa.pid
JOIN 
    AssetPriceView apv ON pa.aid = apv.aid
GROUP BY 
    p.pid, p.uid, p.pname;