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
