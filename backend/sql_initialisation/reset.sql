DROP DATABASE IF EXISTS stock_app;
CREATE DATABASE IF NOT EXISTS stock_app;
USE stock_app;

-- Create User table
CREATE TABLE User (
    uid INT AUTO_INCREMENT PRIMARY KEY,
    uname VARCHAR(100) NOT NULL,
    uemail VARCHAR(100) UNIQUE NOT NULL,
    upno VARCHAR(20),
    equity_funds DECIMAL(10, 2) DEFAULT 0.00,
    commodity_funds DECIMAL(10, 2) DEFAULT 0.00,
    address_id INT
);

-- Create Address table
CREATE TABLE Address (
    address_id INT AUTO_INCREMENT PRIMARY KEY,
    locality VARCHAR(100),
    city VARCHAR(100),
    building VARCHAR(100),
    hno VARCHAR(20)
);

-- Create Nominee table
CREATE TABLE Nominee (
    uid INT,
    nid INT,
    nemail VARCHAR(100),
    ntype VARCHAR(50),
    relation VARCHAR(50),
    nname VARCHAR(100),
    PRIMARY KEY (uid, nid)
);

-- Create Orders table
CREATE TABLE Orders (
    oid INT AUTO_INCREMENT PRIMARY KEY,
    uid INT,
    price DECIMAL(10, 2),
    qty INT,
    date DATE,
    otype VARCHAR(50),
    status VARCHAR(20) DEFAULT 'Pending',
    time TIME
);

-- Create Transaction table
CREATE TABLE Transaction (
    tid INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    status VARCHAR(50),
    uid INT,
    oid INT
);

-- Create Portfolio table
CREATE TABLE Portfolio (
    pid INT AUTO_INCREMENT PRIMARY KEY,
    uid INT,
    pname VARCHAR(100),
    total_val DECIMAL(10, 2) DEFAULT 0.00
);

-- Create Watchlist table
CREATE TABLE Watchlist (
    wid INT AUTO_INCREMENT PRIMARY KEY,
    uid INT,
    wname VARCHAR(100),
    total_val DECIMAL(10, 2) DEFAULT 0.00
);

-- Create Asset table
CREATE TABLE Asset (
    aid INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100)
);

-- Create Price table (to store historical prices)
CREATE TABLE Price (
    aid INT,
    date DATE,
    open_price DECIMAL(10, 2),
    close_price DECIMAL(10, 2),
    high DECIMAL(10, 2),
    low DECIMAL(10, 2),
    volume BIGINT,
    PRIMARY KEY (aid, date)
);

-- Create Portfolio_Asset table
CREATE TABLE Portfolio_Asset (
    pid INT,
    aid INT,
    PRIMARY KEY (pid, aid)
);

-- Create Watchlist_Asset table
CREATE TABLE Watchlist_Asset (
    wid INT,
    aid INT,
    PRIMARY KEY (wid, aid)
);

-- Create Transaction_Asset table
CREATE TABLE Transaction_Asset (
    tid INT,
    aid INT,
    qty INT,
    PRIMARY KEY (tid, aid)
);

-- Add foreign key to User table for Address
ALTER TABLE User
ADD CONSTRAINT fk_user_address FOREIGN KEY (address_id) REFERENCES Address(address_id);

-- Add foreign key to Nominee table for User
ALTER TABLE Nominee
ADD CONSTRAINT fk_nominee_user FOREIGN KEY (uid) REFERENCES User(uid);

-- Add foreign keys to Orders table for User
ALTER TABLE Orders
ADD CONSTRAINT fk_orders_user FOREIGN KEY (uid) REFERENCES User(uid);

-- Add foreign keys to Transaction table for User and Orders
ALTER TABLE Transaction
ADD CONSTRAINT fk_transaction_user FOREIGN KEY (uid) REFERENCES User(uid),
ADD CONSTRAINT fk_transaction_orders FOREIGN KEY (oid) REFERENCES Orders(oid);

-- Add foreign key to Portfolio table for User
ALTER TABLE Portfolio
ADD CONSTRAINT fk_portfolio_user FOREIGN KEY (uid) REFERENCES User(uid);

-- Add foreign key to Watchlist table for User
ALTER TABLE Watchlist
ADD CONSTRAINT fk_watchlist_user FOREIGN KEY (uid) REFERENCES User(uid);

-- Add foreign keys to Portfolio_Asset table for Portfolio and Asset
ALTER TABLE Portfolio_Asset
ADD CONSTRAINT fk_portfolio_asset_portfolio FOREIGN KEY (pid) REFERENCES Portfolio(pid),
ADD CONSTRAINT fk_portfolio_asset_asset FOREIGN KEY (aid) REFERENCES Asset(aid);

-- Add foreign keys to Watchlist_Asset table for Watchlist and Asset
ALTER TABLE Watchlist_Asset
ADD CONSTRAINT fk_watchlist_asset_watchlist FOREIGN KEY (wid) REFERENCES Watchlist(wid),
ADD CONSTRAINT fk_watchlist_asset_asset FOREIGN KEY (aid) REFERENCES Asset(aid);

-- Add foreign keys to Transaction_Asset table for Transaction and Asset
ALTER TABLE Transaction_Asset
ADD CONSTRAINT fk_transaction_asset_transaction FOREIGN KEY (tid) REFERENCES Transaction(tid),
ADD CONSTRAINT fk_transaction_asset_asset FOREIGN KEY (aid) REFERENCES Asset(aid);
