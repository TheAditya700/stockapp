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




