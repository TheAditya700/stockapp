DELIMITER $$

-- 1. Calculate Portfolio Value
CREATE FUNCTION calculate_portfolio_value(uid INT)
RETURNS DECIMAL(15,2)
DETERMINISTIC
BEGIN
    DECLARE total_value DECIMAL(15,2) DEFAULT 0;
    DECLARE asset_value DECIMAL(15,2);
    DECLARE done INT DEFAULT 0;
    DECLARE cur_aid INT;
    DECLARE cur_qty INT;
    DECLARE cur_price DECIMAL(10,2);

    DECLARE asset_cursor CURSOR FOR
    SELECT p.aid, p.qty, apv.current_price -- Fixed to use AssetPriceView
    FROM Portfolio_Asset p
    JOIN AssetPriceView apv ON p.aid = apv.aid
    WHERE (SELECT p2.uid FROM Portfolio p2 WHERE p2.pid = p.pid) = uid;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN asset_cursor;
    read_loop: LOOP
        FETCH asset_cursor INTO cur_aid, cur_qty, cur_price;
        IF done THEN
            LEAVE read_loop;
        END IF;
        SET asset_value = cur_qty * cur_price;
        SET total_value = total_value + asset_value;
    END LOOP;
    CLOSE asset_cursor;
    RETURN total_value;
END$$

-- 2. Pending Cost Equity
CREATE FUNCTION GetTotalPendingCostEquity(uid INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total_cost DECIMAL(10,2);
    SELECT COALESCE(SUM(price * qty), 0) INTO total_cost
    FROM Orders
    JOIN Asset ON Orders.aid = Asset.aid
    WHERE Orders.uid = uid AND Orders.status = 'Pending' AND Asset.asset_type = 'Equity';
    RETURN total_cost;
END$$

-- 3. Pending Cost Commodity
CREATE FUNCTION GetTotalPendingCostCommodity(uid INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total_cost DECIMAL(10,2);
    SELECT COALESCE(SUM(price * qty), 0) INTO total_cost
    FROM Orders
    JOIN Asset ON Orders.aid = Asset.aid
    WHERE Orders.uid = uid AND Orders.status = 'Pending' AND Asset.asset_type = 'Commodity';
    RETURN total_cost;
END$$

-- 4. Total Cost Equity
CREATE FUNCTION GetTotalCostEquity(uid INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total_cost DECIMAL(10,2);
    SELECT COALESCE(SUM(price * qty), 0) INTO total_cost
    FROM Orders
    JOIN Asset ON Orders.aid = Asset.aid
    WHERE Orders.uid = uid AND Asset.asset_type = 'Equity';
    RETURN total_cost;
END$$

-- 5. Total Cost Commodity
CREATE FUNCTION GetTotalCostCommodity(uid INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total_cost DECIMAL(10,2);
    SELECT COALESCE(SUM(price * qty), 0) INTO total_cost
    FROM Orders
    JOIN Asset ON Orders.aid = Asset.aid
    WHERE Orders.uid = uid AND Asset.asset_type = 'Commodity';
    RETURN total_cost;
END$$

DELIMITER ;