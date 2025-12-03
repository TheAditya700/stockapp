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
