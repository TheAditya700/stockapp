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

ALTER TABLE Portfolio DROP COLUMN total_val;

CREATE OR REPLACE VIEW AssetPriceView AS
SELECT 
    a.aid, 
    a.name, 
    a.asset_type,        -- Include asset_type from Asset table
    p.close_price AS current_price
FROM 
    Asset a
JOIN 
    Price p ON a.aid = p.aid
JOIN 
    (SELECT aid, MAX(date) AS latest_date FROM Price GROUP BY aid) AS latest_prices
    ON p.aid = latest_prices.aid AND p.date = latest_prices.latest_date;



ALTER TABLE Portfolio_Asset
ADD COLUMN qty INT NOT NULL DEFAULT 0;

CREATE VIEW PortfolioTotalValueView AS
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

ALTER TABLE Asset
ADD COLUMN asset_type ENUM('Equity', 'Commodity') NOT NULL DEFAULT 'Equity';



DELIMITER $$

DROP TRIGGER IF EXISTS update_funds_after_transaction;

CREATE TRIGGER update_funds_after_transaction
AFTER INSERT ON Transaction
FOR EACH ROW
BEGIN
    DECLARE asset_type VARCHAR(20);
    DECLARE aid INT;

    -- Fetch the asset ID (aid) from the Orders table using buy_oid from the new transaction
    SELECT o.aid INTO aid
    FROM Orders o
    WHERE o.oid = NEW.buy_oid
    LIMIT 1;

    -- Determine the asset type (Equity or Commodity) from the Asset table based on the aid
    SELECT asset_type INTO asset_type
    FROM Asset
    WHERE aid = aid
    LIMIT 1;

    -- Update buyer and seller funds based on the asset type
    IF asset_type = 'Equity' THEN
        -- Update buyer's equity funds
        UPDATE `User`
        SET equity_funds = equity_funds - (NEW.qty * NEW.price)
        WHERE uid = NEW.buy_uid;

        -- Update seller's equity funds
        UPDATE `User`
        SET equity_funds = equity_funds + (NEW.qty * NEW.price)
        WHERE uid = NEW.sell_uid;
    ELSEIF asset_type = 'Commodity' THEN
        -- Update buyer's commodity funds
        UPDATE `User`
        SET commodity_funds = commodity_funds - (NEW.qty * NEW.price)
        WHERE uid = NEW.buy_uid;

        -- Update seller's commodity funds
        UPDATE `User`
        SET commodity_funds = commodity_funds + (NEW.qty * NEW.price)
        WHERE uid = NEW.sell_uid;
    END IF;
END $$

DELIMITER ;

CREATE TRIGGER insert_portfolio_after_user
AFTER INSERT ON `User`
FOR EACH ROW
BEGIN
    -- Insert a new portfolio for the new user with their uname as pname
    INSERT INTO `Portfolio` (uid, pname)
    VALUES (NEW.uid, CONCAT(NEW.uname, "'s Portfolio"));
END;

CREATE ROLE 'admin';
CREATE ROLE 'user';

GRANT SELECT, INSERT, UPDATE ON `User` TO 'user';
GRANT SELECT, INSERT, UPDATE ON `Portfolio` TO 'user';
GRANT SELECT, INSERT, UPDATE ON `Watchlist` TO 'user';
GRANT SELECT, INSERT, UPDATE ON `Watchlist_Asset` TO 'user';
GRANT SELECT, INSERT, UPDATE ON `Orders` TO 'user';
GRANT SELECT, INSERT, UPDATE ON `Portfolio_Asset` TO 'user';
GRANT SELECT ON `Asset` TO 'user';

GRANT ALL PRIVILEGES ON *.* TO 'admin' WITH GRANT OPTION;


-- Create user1 and assign the 'user' role
CREATE USER 'user1'@'localhost' IDENTIFIED BY 'password1';
GRANT 'user' TO 'user1'@'localhost';

-- Create user2 and assign the 'admin' role
CREATE USER 'admin1'@'localhost' IDENTIFIED BY 'password2';
GRANT 'admin' TO 'admin1'@'localhost';

USE stock_app;

DROP PROCEDURE IF EXISTS place_order;

DELIMITER $$

CREATE PROCEDURE place_order(
    IN uid INT, 
    IN asset_id INT,
    IN qty INT, 
    IN otype VARCHAR(50)
)
BEGIN
    DECLARE asset_price DECIMAL(10,2);

    -- Get the current price from AssetPriceView
    SELECT current_price INTO asset_price
    FROM AssetPriceView
    WHERE aid = asset_id
    LIMIT 1;

    -- Insert the new order
    INSERT INTO `Orders` (uid, aid, qty, price, otype, status, date, time)
    VALUES (uid, asset_id, qty, asset_price, otype, 'Pending', CURDATE(), CURTIME());
END$$

DELIMITER ;

DROP PROCEDURE IF EXISTS MatchOrders;

DELIMITER $$

CREATE PROCEDURE MatchOrders()
BEGIN
    DECLARE done INT DEFAULT 0;

    -- Variables for Buy and Sell orders
    DECLARE buy_oid INT;
    DECLARE buy_uid INT;
    DECLARE buy_price DECIMAL(10,2);
    DECLARE buy_qty INT;
    DECLARE buy_aid INT;
    DECLARE sell_oid INT;
    DECLARE sell_uid INT;
    DECLARE sell_price DECIMAL(10,2);
    DECLARE sell_qty INT;
    DECLARE sell_aid INT;

    -- Variables for remaining quantities
    DECLARE remaining_buy_qty INT;
    DECLARE remaining_sell_qty INT;

    -- Variables to store new completed order IDs
    DECLARE new_buy_oid INT;
    DECLARE new_sell_oid INT;

    -- Cursor for matching orders
    DECLARE order_cur CURSOR FOR
        SELECT b.oid, b.uid, b.price, b.qty, b.aid, s.oid, s.uid, s.price, s.qty, s.aid
        FROM Orders b
        JOIN Orders s 
            ON b.aid = s.aid
           AND b.otype = 'Buy' AND s.otype = 'Sell'
           AND b.status = 'Pending' AND s.status = 'Pending'
           AND b.price >= s.price;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- Open the cursor
    OPEN order_cur;

    match_loop: LOOP
        FETCH order_cur INTO buy_oid, buy_uid, buy_price, buy_qty, buy_aid, 
                             sell_oid, sell_uid, sell_price, sell_qty, sell_aid;

        IF done THEN
            LEAVE match_loop;
        END IF;

        -- Initialize remaining quantities
        SET remaining_buy_qty = buy_qty;
        SET remaining_sell_qty = sell_qty;

        -- Calculate the transacted quantity
        SET @trans_qty = LEAST(remaining_buy_qty, remaining_sell_qty);

        -- Insert completed Buy order
        INSERT INTO Orders (uid, price, qty, date, otype, status, aid)
        VALUES (buy_uid, buy_price, @trans_qty, CURDATE(), 'Buy', 'Completed', buy_aid);
        SET new_buy_oid = LAST_INSERT_ID();

        -- Insert completed Sell order
        INSERT INTO Orders (uid, price, qty, date, otype, status, aid)
        VALUES (sell_uid, sell_price, @trans_qty, CURDATE(), 'Sell', 'Completed', sell_aid);
        SET new_sell_oid = LAST_INSERT_ID();

        -- Update Portfolio_Asset for the buyer
        INSERT INTO Portfolio_Asset (pid, aid, qty, buy_price)
        VALUES (
            (SELECT pid FROM Portfolio WHERE uid = buy_uid), 
            buy_aid, 
            @trans_qty, 
            buy_price
        )
        ON DUPLICATE KEY UPDATE 
            qty = qty + @trans_qty,
            buy_price = ((buy_price * qty) + (@trans_qty * VALUES(buy_price))) / (qty + @trans_qty);

        -- Update Portfolio_Asset for the seller
        INSERT INTO Portfolio_Asset (pid, aid, qty, buy_price)
        VALUES (
            (SELECT pid FROM Portfolio WHERE uid = sell_uid), 
            sell_aid, 
            -@trans_qty, 
            sell_price
        )
        ON DUPLICATE KEY UPDATE 
            qty = qty - @trans_qty;

        -- Insert transaction with new completed order IDs
        INSERT INTO Transaction (date, buy_oid, sell_oid, buy_uid, sell_uid, price, qty)
        VALUES (CURDATE(), new_buy_oid, new_sell_oid, buy_uid, sell_uid, sell_price, @trans_qty);

        -- Update remaining quantities
        SET remaining_buy_qty = remaining_buy_qty - @trans_qty;
        SET remaining_sell_qty = remaining_sell_qty - @trans_qty;

        -- Update original Buy order
        UPDATE Orders
        SET qty = qty - @trans_qty
        WHERE oid = buy_oid;

        -- Update original Sell order
        UPDATE Orders
        SET qty = qty - @trans_qty
        WHERE oid = sell_oid;

        -- Delete any pending orders with qty = 0
        DELETE FROM Orders
        WHERE qty = 0 AND status = 'Pending';

        -- Stop matching if either order is fully fulfilled
        IF remaining_buy_qty = 0 OR remaining_sell_qty = 0 THEN
            LEAVE match_loop;
        END IF;
    END LOOP;

    CLOSE order_cur;
END$$

DELIMITER ;


DELIMITER $$

CREATE FUNCTION calculate_portfolio_value(uid INT)
RETURNS DECIMAL(15,2)
DETERMINISTIC
BEGIN
    DECLARE total_value DECIMAL(15,2) DEFAULT 0;
    DECLARE asset_value DECIMAL(15,2);

    -- Cursor to loop through all assets in the user's portfolio
    DECLARE done INT DEFAULT 0;
    DECLARE cur_aid INT;
    DECLARE cur_qty INT;
    DECLARE cur_price DECIMAL(10,2);

    -- Cursor to get all assets in the user's portfolio with their quantity
    DECLARE asset_cursor CURSOR FOR
    SELECT p.aid, p.qty, a.price
    FROM Portfolio_Asset p
    JOIN Asset a ON p.aid = a.aid
    WHERE p.uid = uid;

    -- Continue loop handler
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- Open the cursor
    OPEN asset_cursor;

    read_loop: LOOP
        -- Fetch each asset and its quantity and price
        FETCH asset_cursor INTO cur_aid, cur_qty, cur_price;
        
        -- Exit the loop if no more rows
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Calculate the asset value and add it to the total portfolio value
        SET asset_value = cur_qty * cur_price;
        SET total_value = total_value + asset_value;
    END LOOP;

    -- Close the cursor
    CLOSE asset_cursor;

    -- Return the total portfolio value
    RETURN total_value;
END$$

DELIMITER ;

DELIMITER $$

-- Function to calculate total pending cost for equity orders
CREATE FUNCTION GetTotalPendingCostEquity(uid INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total_cost DECIMAL(10,2);
    -- Fetch the total pending cost for equity (use COALESCE to handle NULL)
    SELECT COALESCE(SUM(price * qty), 0) INTO total_cost
    FROM Orders
    JOIN Asset ON Orders.aid = Asset.aid
    WHERE Orders.uid = uid AND Orders.status = 'Pending' AND Asset.asset_type = 'Equity';
    RETURN total_cost;
END$$

-- Function to calculate total pending cost for commodity orders
CREATE FUNCTION GetTotalPendingCostCommodity(uid INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total_cost DECIMAL(10,2);
    -- Fetch the total pending cost for commodity (use COALESCE to handle NULL)
    SELECT COALESCE(SUM(price * qty), 0) INTO total_cost
    FROM Orders
    JOIN Asset ON Orders.aid = Asset.aid
    WHERE Orders.uid = uid AND Orders.status = 'Pending' AND Asset.asset_type = 'Commodity';
    RETURN total_cost;
END$$

DELIMITER ;

DELIMITER $$

DELIMITER ;

DELIMITER $$

-- Function to get total cost for equity orders
CREATE FUNCTION GetTotalCostEquity(uid INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total_cost DECIMAL(10,2);
    -- Fetch the total cost for equity orders
    SELECT COALESCE(SUM(price * qty), 0) INTO total_cost
    FROM Orders
    JOIN Asset ON Orders.aid = Asset.aid
    WHERE Orders.uid = uid AND Asset.asset_type = 'Equity';
    RETURN total_cost;
END$$

-- Function to get total cost for commodity orders
CREATE FUNCTION GetTotalCostCommodity(uid INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total_cost DECIMAL(10,2);
    -- Fetch the total cost for commodity orders
    SELECT COALESCE(SUM(price * qty), 0) INTO total_cost
    FROM Orders
    JOIN Asset ON Orders.aid = Asset.aid
    WHERE Orders.uid = uid AND Asset.asset_type = 'Commodity';
    RETURN total_cost;
END$$


DELIMITER ;


