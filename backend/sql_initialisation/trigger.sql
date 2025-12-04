DELIMITER $$

-- 1. Update Funds after Transaction
CREATE TRIGGER update_funds_after_transaction
AFTER INSERT ON Transaction
FOR EACH ROW
BEGIN
    DECLARE asset_type_var VARCHAR(20);
    DECLARE aid_var INT;

    -- Get Asset ID from the Buy Order
    SELECT aid INTO aid_var FROM Orders WHERE oid = NEW.buy_oid LIMIT 1;

    -- Get Asset Type
    SELECT asset_type INTO asset_type_var FROM Asset WHERE aid = aid_var LIMIT 1;

    IF asset_type_var = 'Equity' THEN
        UPDATE `User` SET equity_funds = equity_funds - (NEW.qty * NEW.price) WHERE uid = NEW.buy_uid;
        UPDATE `User` SET equity_funds = equity_funds + (NEW.qty * NEW.price) WHERE uid = NEW.sell_uid;
    ELSEIF asset_type_var = 'Commodity' THEN
        UPDATE `User` SET commodity_funds = commodity_funds - (NEW.qty * NEW.price) WHERE uid = NEW.buy_uid;
        UPDATE `User` SET commodity_funds = commodity_funds + (NEW.qty * NEW.price) WHERE uid = NEW.sell_uid;
    END IF;
END$$

-- 2. Create Portfolio after User Registration
CREATE TRIGGER insert_portfolio_after_user
AFTER INSERT ON `User`
FOR EACH ROW
BEGIN
    INSERT INTO `Portfolio` (uid, pname)
    VALUES (NEW.uid, CONCAT(NEW.uname, "'s Portfolio"));
END$$

DELIMITER ;