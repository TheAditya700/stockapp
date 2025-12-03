show databases;
use stock_app;

select * from Asset;

show tables;

select * from Price;

DELETE t1 FROM Asset t1
INNER JOIN Asset t2 
WHERE t1.aid > t2.aid 
AND t1.name = t2.name;

ALTER TABLE Asset
ADD CONSTRAINT UNIQUE (name);

SELECT aid, COUNT(*) AS price_count
FROM Price
GROUP BY aid;

UPDATE Asset SET asset_type = 'Equity'

TRUNCATE TABLE Portfolio_Asset;

ALTER TABLE Portfolio DROP COLUMN total_val;
DROP VIEW IF EXISTS PortfolioTotalValueView;

CREATE VIEW PortfolioTotalValueView AS
SELECT 
    p.pid, 
    p.uid, 
    p.pname,
    SUM(pa.qty * ap.current_price) AS total_value
FROM Portfolio p
JOIN Portfolio_Asset pa ON p.pid = pa.pid
JOIN AssetPriceView ap ON pa.aid = ap.aid
GROUP BY p.pid;

select * from Portfolio;

desc Portfolio;

desc Portfolio_Asset;

select * from Portfolio_Asset;

-- Insert a portfolio for each user if they don't already have one
INSERT INTO Portfolio (uid, pname)
SELECT u.uid, CONCAT(u.uname, "'s Portfolio") AS pname
FROM User u
LEFT JOIN Portfolio p ON u.uid = p.uid
WHERE p.uid IS NULL;  -- Only insert if the user doesn't already have a portfolio

TRUNCATE TABLE Portfolio_Asset;
INSERT INTO Portfolio_Asset (pid, aid, qty)
SELECT p.pid, a.aid, FLOOR(RAND() * 100 + 1) AS qty
FROM Portfolio p
JOIN Asset a ON a.asset_type = 'Equity'
ORDER BY RAND()
LIMIT 100;  -- You can adjust the limit based on how many entries you want to insert

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
    p.uid = 11;
  -- Replace <sample_user_uid> with the user's uid


ALTER TABLE Portfolio_Asset 
ADD COLUMN buy_price DECIMAL(10, 2);
INSERT INTO Portfolio_Asset (pid, aid, qty, buy_price)
SELECT 
    p.pid, 
    a.aid, 
    FLOOR(RAND() * 100 + 1) AS qty,
    (SELECT close_price FROM Price WHERE aid = a.aid ORDER BY RAND() LIMIT 1) AS buy_price  -- Fetch a random price
FROM 
    Portfolio p
JOIN 
    Asset a ON a.asset_type = 'Equity'
ORDER BY 
    RAND()
LIMIT 100;  -- Adjust the limit based on how many entries you want to insert

select * from Asset

show tables;

desc Asset;

desc AssetPriceView;

show tables;

desc Orders;

ALTER TABLE Orders
ADD COLUMN aid INT;

ALTER TABLE Orders
ADD CONSTRAINT fk_orders_asset
FOREIGN KEY (aid) REFERENCES Asset(aid)
ON DELETE CASCADE
ON UPDATE CASCADE;

-- Inserting dummy orders for user with uid = 19
INSERT INTO Orders (uid, aid, price, qty, date, otype, status, time)
VALUES
(19, (SELECT aid FROM Asset WHERE name = 'INFY' LIMIT 1), 1700.50, 10, '2024-10-25', 'Buy', 'Completed', '09:30:00'),
(19, (SELECT aid FROM Asset WHERE name = 'TCS' LIMIT 1), 3500.75, 5, '2024-10-24', 'Sell', 'Completed', '10:15:00'),
(19, (SELECT aid FROM Asset WHERE name = 'RELIANCE' LIMIT 2), 2500.00, 8, '2024-10-23', 'Buy', 'Pending', '11:00:00'),
(19, (SELECT aid FROM Asset WHERE name = 'MARUTI' LIMIT 4), 9000.00, 3, '2024-10-22', 'Buy', 'Completed', '14:45:00'),
(19, (SELECT aid FROM Asset WHERE name = 'TECHM' LIMIT 1), 1709.00, 15, '2024-10-21', 'Sell', 'Completed', '13:20:00');

-- You can repeat this pattern for other users or assets.

show tables;

desc Watchlist;

desc Watchlist_Asset

-- Inserting dummy watchlists for user with uid = 1 (replace with your uid)
INSERT INTO Watchlist (uid, wname, total_val) VALUES (19, 'Tech Stocks Watchlist', 0.00);
INSERT INTO Watchlist (uid, wname, total_val) VALUES (19, 'Energy Sector Watchlist', 0.00);
INSERT INTO Watchlist (uid, wname, total_val) VALUES (19, 'Auto Sector Watchlist', 0.00);

-- Add assets to 'Tech Stocks Watchlist'
INSERT INTO Watchlist_Asset (wid, aid) VALUES ((SELECT wid FROM Watchlist WHERE wname = 'Tech Stocks Watchlist'), (SELECT aid FROM Asset WHERE name = 'INFY'));
INSERT INTO Watchlist_Asset (wid, aid) VALUES ((SELECT wid FROM Watchlist WHERE wname = 'Tech Stocks Watchlist'), (SELECT aid FROM Asset WHERE name = 'TCS'));
INSERT INTO Watchlist_Asset (wid, aid) VALUES ((SELECT wid FROM Watchlist WHERE wname = 'Tech Stocks Watchlist'), (SELECT aid FROM Asset WHERE name = 'WIPRO'));

-- Add assets to 'Energy Sector Watchlist'
INSERT INTO Watchlist_Asset (wid, aid) VALUES ((SELECT wid FROM Watchlist WHERE wname = 'Energy Sector Watchlist'), (SELECT aid FROM Asset WHERE name = 'RELIANCE'));
INSERT INTO Watchlist_Asset (wid, aid) VALUES ((SELECT wid FROM Watchlist WHERE wname = 'Energy Sector Watchlist'), (SELECT aid FROM Asset WHERE name = 'ONGC'));

-- Add assets to 'Auto Sector Watchlist'
INSERT INTO Watchlist_Asset (wid, aid) VALUES ((SELECT wid FROM Watchlist WHERE wname = 'Auto Sector Watchlist'), (SELECT aid FROM Asset WHERE name = 'MARUTI'));
INSERT INTO Watchlist_Asset (wid, aid) VALUES ((SELECT wid FROM Watchlist WHERE wname = 'Auto Sector Watchlist'), (SELECT aid FROM Asset WHERE name = 'TATAMOTORS'));

SHOW FULL TABLES IN stock_app WHERE TABLE_TYPE = 'VIEW';

ALTER TABLE User ADD COLUMN password VARCHAR(200) NOT NULL;

UPDATE User
SET password = 'hashed_password_1'
WHERE uemail = 'amit.sharma@example.com';

UPDATE User
SET password = 'hashed_password_2'
WHERE uemail = 'priya.patel@example.com';

UPDATE User
SET password = 'hashed_password_3'
WHERE uemail = 'priyansh.gupta@example.com';

UPDATE User
SET password = 'hashed_password_4'
WHERE uemail = 'anjali.nair@example.com';

UPDATE User
SET password = 'hashed_password_5'
WHERE uemail = 'vikram.mehta@example.com';

UPDATE User
SET password = 'hashed_password_6'
WHERE uemail = 'deepika.rao@example.com';

UPDATE User
SET password = 'hashed_password_7'
WHERE uemail = 'rohan.k@example.com';

UPDATE User
SET password = 'hashed_password_8'
WHERE uemail = 'simran.singh@example.com';

UPDATE User
SET password = 'hashed_password_9'
WHERE uemail = 'karan.desai@example.com';

UPDATE User
SET password = 'hashed_password_10'
WHERE uemail = 'neha.verma@example.com';

-- Add user 19
INSERT INTO User (uid, uname, uemail, upno, equity_funds, commodity_funds, address_id, password)
VALUES 
(19, 'Sneha Kapoor', 'sneha.kapoor@example.com', '9876543229', 21000.00, 3500.00, 19, 'hashed_password_19');

SELECT * FROM User where uid=19;

SELECT uid, uname, uemail, upno, equity_funds, commodity_funds, password 
            FROM `User`
            WHERE uemail = :email
            LIMIT 1

desc User;

show tables;

select * from Asset;

SELECT oid, qty
FROM `Orders`
WHERE price <= 2709.50    -- Replace <buy_order_price> with your Buy order's price
AND otype = 'Buy'
AND status = 'Pending'
AND aid = 1                -- Replace <asset_id> with the asset ID of the test order
LIMIT 1;

SET @new_order_qty = 10;   -- Quantity of the new order
SET @opposite_qty = 2;                  -- From the matched order
SET @match_qty = LEAST(@new_order_qty, @opposite_qty);

SET @opposite_order_id = 23;   -- Opposite order's ID
UPDATE `Orders`
SET qty = qty - @match_qty,
    status = IF(qty - @match_qty = 0, 'Matched', 'Pending')
WHERE oid = @opposite_order_id;

SET @new_order_id = 3;  -- Replace with the ID of your new order
UPDATE `Orders`
SET qty = qty - @match_qty,
    status = IF(qty - @match_qty = 0, 'Matched', 'Pending')
WHERE oid = @new_order_id;

USE stock_app;

-- Drop the old Transaction table if it exists
-- Temporarily turn off foreign key constraints
SET FOREIGN_KEY_CHECKS = 0;

-- Drop the Transaction_Asset table as it's no longer needed
DROP TABLE IF EXISTS `Transaction_Asset`;

-- Drop the old Transaction table if it exists
DROP TABLE IF EXISTS `Transaction`;

-- Recreate the Transaction table with buy_oid, sell_oid, buy_uid, sell_uid, price, and qty
CREATE TABLE `Transaction` (
    `tid` INT AUTO_INCREMENT PRIMARY KEY,
    `date` DATE,
    `buy_oid` INT,
    `sell_oid` INT,
    `buy_uid` INT,
    `sell_uid` INT,
    `price` DECIMAL(10, 2),
    `qty` INT,
    FOREIGN KEY (buy_oid) REFERENCES `Orders`(oid),
    FOREIGN KEY (sell_oid) REFERENCES `Orders`(oid),
    FOREIGN KEY (buy_uid) REFERENCES `User`(uid),
    FOREIGN KEY (sell_uid) REFERENCES `User`(uid)
);

-- Re-enable foreign key constraints
SET FOREIGN_KEY_CHECKS = 1;


