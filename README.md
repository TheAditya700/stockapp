# StockApp - Financial Asset Management System

A full-stack stock trading application featuring a real-time simulated market environment, portfolio management, and order matching engine. Built with React (Frontend), Flask (Backend), and MySQL (Database).

## 🚀 Quick Start

### Prerequisites
*   Docker & Docker Compose

### Running the Application

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd stockapp
    ```

2.  **Start the application:**
    ```bash
    docker-compose up -d --build
    ```

    *   This command builds the images for the backend, frontend, and ticker service.
    *   It initializes the database with:
        *   50 Equities & 5 Commodities.
        *   10 Dummy Users with addresses.
        *   1 Hour of high-frequency historical random data (10-second intervals).
        *   Random initial portfolios and orders.

3.  **Access the App:**
    *   **Frontend:** [http://localhost:3000](http://localhost:3000)
    *   **Backend API:** [http://localhost:5000](http://localhost:5000)

## 🔑 Default Credentials

The system is pre-loaded with 10 dummy users. You can log in with any of the following emails.

**Default Password for ALL users:** `password123`

| Name | Email | Funds (Equity/Commodity) |
| :--- | :--- | :--- |
| Amit Sharma | `amit.sharma@example.com` | ₹10,000 / ₹5,000 |
| Priya Patel | `priya.patel@example.com` | ₹15,000 / ₹3,000 |
| Priyansh Gupta | `priyansh.gupta@example.com` | ₹20,000 / ₹1,000 |
| Anjali Nair | `anjali.nair@example.com` | ₹12,000 / ₹2,000 |
| Vikram Mehta | `vikram.mehta@example.com` | ₹18,000 / ₹4,000 |
| Deepika Rao | `deepika.rao@example.com` | ₹13,000 / ₹3,500 |
| Rohan Kallumal | `rohan.k@example.com` | ₹22,000 / ₹2,500 |
| Simran Singh | `simran.singh@example.com` | ₹16,000 / ₹4,500 |
| Karan Desai | `karan.desai@example.com` | ₹17,500 / ₹5,000 |
| Neha Verma | `neha.verma@example.com` | ₹14,000 / ₹1,500 |

## ✨ Features

### 1. Real-Time Market Simulation
*   **High-Frequency Data:** Asset prices update every 10 seconds, simulating a live market.
*   **Ticker Service:** A background service runs continuously to generate realistic price movements (OHLC) and volume for both Equities and Commodities.
*   **Historical Data:** Charts display hourly history with 10-second granularity.

### 2. Trading & Order Management
*   **Buy/Sell Orders:** Place market orders for any asset.
*   **Order Matching:** A simulated engine matches Buy and Sell orders based on price and time priority.
*   **Margin Checks:** Automatic validation of available funds (Equity/Commodity) before placing orders.

### 3. Portfolio Management
*   **Real-Time Valuation:** See your total portfolio value update live as market prices change.
*   **Profit/Loss Tracking:** Track P&L per asset and for the entire portfolio.
*   **Holdings:** View detailed breakdown of owned assets.

### 4. User Experience
*   **Interactive Dashboard:** Visual overview of funds, margins, and portfolio distribution.
*   **Watchlists:** Create custom watchlists to track specific sectors (e.g., "Tech Giants", "Auto Sector").
*   **Responsive Design:** Clean, responsive UI with a scrollable sidebar and sticky footer.
*   **Search:** Quickly find assets via the sidebar search.

## 🛠️ Tech Stack

*   **Frontend:** React.js, Chart.js, Bootstrap 5
*   **Backend:** Python, Flask, SQLAlchemy, MySQL Connector
*   **Database:** MySQL 8.0
*   **Containerization:** Docker, Docker Compose

## 📂 Project Structure

```
stockapp/
├── backend/           # Flask API & Data Generators
│   ├── flaskapp/      # App logic, routes, models
│   ├── sql_initialisation/ # SQL Scripts (Triggers, Procedures)
│   └── Dockerfile
├── frontend/          # React Application
│   ├── src/           # Components, Styles
│   └── Dockerfile
├── docker-compose.yml # Service Orchestration
└── README.md          # You are here!
```
