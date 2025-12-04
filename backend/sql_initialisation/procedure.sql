DELIMITER $$

-- 1. Place Order
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

-- 2. Match Orders
CREATE PROCEDURE MatchOrders()
BEGIN
    DECLARE done INT DEFAULT 0;
    
    -- Cursor variables
    DECLARE c_buy_oid INT; DECLARE c_sell_oid INT;
    
    -- Variables for fetching current state inside the loop
    DECLARE cur_buy_qty INT; DECLARE cur_sell_qty INT;
    DECLARE cur_buy_price DECIMAL(10,2); DECLARE cur_sell_price DECIMAL(10,2);
    DECLARE cur_buy_uid INT; DECLARE cur_sell_uid INT;
    DECLARE cur_buy_aid INT; DECLARE cur_sell_aid INT;
    
    -- Transaction variables
    DECLARE trans_qty INT;
    DECLARE new_buy_oid INT;
    DECLARE new_sell_oid INT;

    -- Cursor: Find all POTENTIAL matches based on price.
    -- We assume price priority logic is satisfied by the query conditions.
    DECLARE order_cur CURSOR FOR
        SELECT b.oid, s.oid
        FROM Orders b
        JOIN Orders s 
            ON b.aid = s.aid
           AND b.otype = 'Buy' AND s.otype = 'Sell'
           AND b.status = 'Pending' AND s.status = 'Pending'
           AND b.price >= s.price
        ORDER BY b.date ASC, b.time ASC; -- FIFO processing

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN order_cur;

    match_loop: LOOP
        FETCH order_cur INTO c_buy_oid, c_sell_oid;
        IF done THEN LEAVE match_loop; END IF;

        -- CRITICAL FIX: Re-fetch current quantities to ensure they haven't been used up
        -- by a previous iteration of this loop.
        SELECT qty, price, uid, aid INTO cur_buy_qty, cur_buy_price, cur_buy_uid, cur_buy_aid
        FROM Orders WHERE oid = c_buy_oid AND status = 'Pending';

        SELECT qty, price, uid, aid INTO cur_sell_qty, cur_sell_price, cur_sell_uid, cur_sell_aid
        FROM Orders WHERE oid = c_sell_oid AND status = 'Pending';

        -- If either order is fully filled (NULL or 0), skip this match
        IF cur_buy_qty IS NULL OR cur_sell_qty IS NULL OR cur_buy_qty <= 0 OR cur_sell_qty <= 0 THEN
            ITERATE match_loop;
        END IF;

        -- Calculate transaction quantity
        SET trans_qty = LEAST(cur_buy_qty, cur_sell_qty);

        -- Insert completed Buy order
        INSERT INTO Orders (uid, price, qty, date, time, otype, status, aid)
        VALUES (cur_buy_uid, cur_buy_price, trans_qty, CURDATE(), CURTIME(), 'Buy', 'Completed', cur_buy_aid);
        SET new_buy_oid = LAST_INSERT_ID();

        -- Insert completed Sell order
        INSERT INTO Orders (uid, price, qty, date, time, otype, status, aid)
        VALUES (cur_sell_uid, cur_sell_price, trans_qty, CURDATE(), CURTIME(), 'Sell', 'Completed', cur_sell_aid);
        SET new_sell_oid = LAST_INSERT_ID();

        -- Update Portfolio (Buyer)
        INSERT INTO Portfolio_Asset (pid, aid, qty, buy_price)
        VALUES ((SELECT pid FROM Portfolio WHERE uid = cur_buy_uid), cur_buy_aid, trans_qty, cur_buy_price)
        ON DUPLICATE KEY UPDATE 
            buy_price = ((buy_price * qty) + (trans_qty * VALUES(buy_price))) / (qty + trans_qty),
            qty = qty + trans_qty;

        -- Update Portfolio (Seller)
        INSERT INTO Portfolio_Asset (pid, aid, qty, buy_price)
        VALUES ((SELECT pid FROM Portfolio WHERE uid = cur_sell_uid), cur_sell_aid, -trans_qty, cur_sell_price)
        ON DUPLICATE KEY UPDATE qty = qty - trans_qty;

        -- Record Transaction
        INSERT INTO Transaction (date, buy_oid, sell_oid, buy_uid, sell_uid, price, qty)
        VALUES (CURDATE(), new_buy_oid, new_sell_oid, cur_buy_uid, cur_sell_uid, cur_sell_price, trans_qty);

        -- Update original pending orders
        UPDATE Orders SET qty = qty - trans_qty WHERE oid = c_buy_oid;
        UPDATE Orders SET qty = qty - trans_qty WHERE oid = c_sell_oid;

        -- Cleanup 0 qty pending orders
        DELETE FROM Orders WHERE qty = 0 AND status = 'Pending' AND (oid = c_buy_oid OR oid = c_sell_oid);

    END LOOP;

    CLOSE order_cur;
END$$

DELIMITER ;