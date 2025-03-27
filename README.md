# Financial Asset Management System (FAMS)

## Overview

The **Financial Asset Management System (FAMS)** is a robust, web-based application designed for portfolio management, risk assessment, and goal-based financial planning. This system enables users to manage their investments, track portfolio performance, optimize risk, and access real-time market data. It offers powerful tools for investors, advisors, and institutional users, allowing them to make data-driven decisions efficiently.

This project was developed as part of a **DBMS - SE Project** and follows the **Agile Scrum** methodology.

## Features

- **Portfolio Management:** Create, update, and view investment portfolios.
- **Risk Assessment and Optimization:** Evaluate portfolio risk and provide recommendations to minimize risk and maximize returns.
- **Goal-Based Planning:** Set and track financial goals linked to user portfolios.
- **Real-Time Market Data Integration:** Fetch real-time financial data from external APIs for accurate decision-making.
- **Reporting and Analysis:** Generate detailed performance reports and analyze investment strategies.

## Key Functionalities

1. **Portfolio Management:**
   - Create and view personal portfolios.
   - Calculate and display portfolio values based on real-time market data.
   - Manage multiple portfolios for different users.

2. **Risk Assessment:**
   - Evaluate portfolio risk based on asset allocation.
   - Provide optimization recommendations to improve portfolio performance.

3. **Goal-Based Planning:**
   - Set and track financial goals such as retirement savings or investment targets.
   - Provide progress tracking towards achieving these goals.

4. **Real-Time Market Data Integration:**
   - Integrate with external financial APIs to pull the latest market data (stocks, bonds, etc.).

5. **Reporting and Analytics:**
   - Generate detailed performance reports of portfolios.
   - Analyze the effectiveness of investment strategies.

## System Architecture

The system is built using a **three-tier architecture**:

1. **Frontend:** A dynamic user interface built with React.js that allows users to interact with their portfolios, assets, and perform financial analysis.
2. **Backend:** Developed in Python using the Flask framework for efficient handling of API requests and database operations.
3. **Database:** A MySQL relational database that stores data on users, portfolios, assets, orders, transactions, and more.

## Tools and Technologies Used

- **Frontend:** React.js
- **Backend:** Python, Flask
- **Database:** MySQL
- **Version Control:** Git, GitHub

## Database Schema

The database includes several important tables to manage users, assets, portfolios, orders, transactions, and more:

- **User**: Stores user information (UID, name, email, funds, etc.)
- **Portfolio**: Stores portfolio data (PID, user ID, portfolio name, etc.)
- **Asset**: Stores asset information (asset type, name, price)
- **Order**: Handles the orders placed by users for buying and selling assets
- **Transaction**: Manages transaction records including buying and selling actions
- **Watchlist**: Allows users to create and manage custom watchlists for assets
- **Price**: Stores historical price data of assets

### Example Table

```sql
CREATE TABLE User (
    uid INT AUTO_INCREMENT PRIMARY KEY,
    uname VARCHAR(100),
    uemail VARCHAR(100) UNIQUE,
    equity_funds DECIMAL(10, 2),
    commodity_funds DECIMAL(10, 2),
    address_id INT
);
```
## Setup and Installation

To set up this project locally, follow these steps:

### Prerequisites
1. Install [Node.js](https://nodejs.org/en/) for frontend development.
2. Install [Python](https://www.python.org/downloads/) and [Flask](https://flask.palletsprojects.com/) for backend development.
3. Install [MySQL](https://www.mysql.com/) for database management.

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/TheAditya700/stockapp.git
   ```
2. Navigate to the project directory:
   ```bash
   cd stockapp
   ```
3. Install frontend dependencies:
   ```bash
   npm install
   ```
4. Set up the backend:
   ```bash
   pip install -r requirements.txt
   ```
5. Create and configure the MySQL database as per the schema provided in the repository.

6. Run the application:
   - Start the frontend:
     ```bash
     npm start
     ```
   - Start the backend:
     ```bash
     python app.py
     ```

## PDF Documentation

For detailed project documentation, please refer to the [Financial Asset Management System PDF](Financial_Asset_Management_System.pdf).
