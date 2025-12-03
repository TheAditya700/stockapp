USE stock_app;

-- Insert dummy addresses into the Address table
INSERT INTO Address (locality, city, building, hno)
VALUES 
('MG Road', 'Bangalore', 'Brigade Towers', '12'),
('Andheri', 'Mumbai', 'Sea Breeze Apartments', '23B'),
('Salt Lake', 'Kolkata', 'Infinity Towers', '45A'),
('Jubilee Hills', 'Hyderabad', 'Sunrise Residency', '67'),
('Connaught Place', 'Delhi', 'Royal Apartments', '34'),
('Viman Nagar', 'Pune', 'Skyline Towers', '22'),
('Banjara Hills', 'Hyderabad', 'Hilltop Villas', '101'),
('Sector 18', 'Noida', 'Silver Residency', '89'),
('Park Street', 'Kolkata', 'Galaxy Towers', '56A'),
('Koramangala', 'Bangalore', 'Eagle Apartments', '77');


-- Insert dummy users into the User table with Indian names
INSERT INTO User (uname, uemail, upno, equity_funds, commodity_funds, address_id)
VALUES 
('Amit Sharma', 'amit.sharma@example.com', '9876543210', 10000.00, 5000.00, 1),
('Priya Patel', 'priya.patel@example.com', '9876543211', 15000.00, 3000.00, 2),
('Priyansh Gupta', 'priyansh.gupta@example.com', '9876543212', 20000.00, 1000.00, 3),
('Anjali Nair', 'anjali.nair@example.com', '9876543213', 12000.00, 2000.00, 4),
('Vikram Mehta', 'vikram.mehta@example.com', '9876543214', 18000.00, 4000.00, 5),
('Deepika Rao', 'deepika.rao@example.com', '9876543215', 13000.00, 3500.00, 6),
('Rohan Kallumal', 'rohan.k@example.com', '9876543216', 22000.00, 2500.00, 7),
('Simran Singh', 'simran.singh@example.com', '9876543217', 16000.00, 4500.00, 8),
('Karan Desai', 'karan.desai@example.com', '9876543218', 17500.00, 5000.00, 9),
('Neha Verma', 'neha.verma@example.com', '9876543219', 14000.00, 1500.00, 10);
