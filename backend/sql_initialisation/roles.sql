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
