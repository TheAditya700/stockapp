import React, { useEffect, useState } from 'react';
import { Pie } from 'react-chartjs-2';
import 'chart.js/auto';

const Home = ({ userData }) => {
  const [availableMarginEquity, setAvailableMarginEquity] = useState(null);
  const [availableMarginCommodity, setAvailableMarginCommodity] = useState(null);
  const [utilizedMarginEquity, setUtilizedMarginEquity] = useState(0);
  const [utilizedMarginCommodity, setUtilizedMarginCommodity] = useState(0);
  const [portfolioValue, setPortfolioValue] = useState(0);
  const [totalProfit, setTotalProfit] = useState(0);
  const [profitPercentage, setProfitPercentage] = useState("0.00");
  const [loading, setLoading] = useState(true);
  const [totalEquityValue, setTotalEquityValue] = useState(0);
  const [totalCommodityValue, setTotalCommodityValue] = useState(0);

  const equity = userData ? Number(userData.equity_funds) || 0 : 0;
  const commodity = userData ? Number(userData.commodity_funds) || 0 : 0;
  const userName = userData ? userData.uname : 'User';

  // Format number with Rupee symbol in Indian numbering system
  const formatNumber = (number) => {
    const formatted = new Intl.NumberFormat('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(number);
    return `₹${formatted}`;
  };

  const fetchData = () => {
    if (userData && userData.uid) {
      setLoading(true); // Reset loading state on visibility
      fetch(`http://127.0.0.1:5000/api/user/${userData.uid}/funds_status`)
        .then((res) => res.json())
        .then((data) => {
          const { available_margin_equity, available_margin_commodity, total_pending_cost_equity, total_pending_cost_commodity, utilized_margin_equity, utilized_margin_commodity } = data;

          setAvailableMarginEquity(available_margin_equity);
          setAvailableMarginCommodity(available_margin_commodity);
          setUtilizedMarginEquity(utilized_margin_equity); // Set utilized margin for equity
          setUtilizedMarginCommodity(utilized_margin_commodity); // Set utilized margin for commodity

          // Fetch the total portfolio value
          fetch(`http://127.0.0.1:5000/api/user/${userData.uid}/portfolio_value`)
            .then((res) => res.json())
            .then((data) => {
              setPortfolioValue(data.total_portfolio_value || 0);
            })
            .catch((error) => {
              console.error('Error fetching portfolio value:', error);
            });

          // Fetch the total portfolio profit and profit percentage
          fetch(`http://127.0.0.1:5000/api/portfolio/summary/${userData.uid}`)
            .then((res) => res.json())
            .then((data) => {
              setTotalProfit(data.total_profit || 0);
              setProfitPercentage(data.total_profit_percentage?.toFixed(2) || "0.00");
              setLoading(false);
            })
            .catch((error) => {
              console.error('Error fetching portfolio summary:', error);
              setLoading(false);
            });
        })
        .catch((error) => {
          console.error('Error fetching funds status:', error);
        });

      // Fetch total equity value and total commodity value
      fetch(`http://127.0.0.1:5000/api/user/${userData.uid}/total_values`)
        .then((res) => res.json())
        .then((data) => {
          setTotalEquityValue(data.total_equity_value || 0);
          setTotalCommodityValue(data.total_commodity_value || 0);
        })
        .catch((error) => {
          console.error('Error fetching total values:', error);
        });
    }
  };

  // Fetch data when component mounts
  useEffect(() => {
    fetchData();
  }, [userData]);

  // Re-fetch data when the page becomes visible
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        fetchData(); // Re-fetch data when the page is visible
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [userData]);

  const pieData = {
    labels: ['Equity', 'Commodity'],
    datasets: [
      {
        data: [totalEquityValue, totalCommodityValue], // Use total equity and commodity values here
        backgroundColor: ['#36A2EB', '#FF6384'],
        hoverBackgroundColor: ['#36A2EB', '#FF6384']
      }
    ]
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container my-4">
      <h1 className="mb-4">Hi, {userName}</h1>

      <div className="row mb-4">
        {/* Equity Card */}
        <div className="col-md-3">
          <div className="card text-center">
            <div className="card-body">
              <h5 className="card-title">Equity</h5>
              <h2>{formatNumber(availableMarginEquity)}</h2>
              <p>Margin Available</p>
              <p>Funds: {formatNumber(equity)}</p>
              <p>Utilized Margin: {formatNumber(utilizedMarginEquity)}</p>
            </div>
          </div>
        </div>

        {/* Commodity Card */}
        <div className="col-md-3">
          <div className="card text-center">
            <div className="card-body">
              <h5 className="card-title">Commodity</h5>
              <h2>{formatNumber(availableMarginCommodity)}</h2>
              <p>Margin Available</p>
              <p>Funds: {formatNumber(commodity)}</p>
              <p>Utilized Margin: {formatNumber(utilizedMarginCommodity)}</p>
            </div>
          </div>
        </div>

        {/* Total Profit and Portfolio Value Card */}
        <div className="col-md-3">
          <div className="card text-center">
            <div className="card-body">
              <h5 className="card-title">Total Portfolio Value</h5>
              <h2>{formatNumber(portfolioValue)}</h2>
              <p>Total Profit: <span style={{ color: totalProfit >= 0 ? 'green' : 'red' }}>{formatNumber(totalProfit)}</span></p>
              <p>Profit Percentage: {profitPercentage}%</p>
            </div>
          </div>
        </div>

        {/* Portfolio Distribution Chart */}
        <div className="col-md-3">
          <div className="card text-center">
            <div className="card-body">
              <h5 className="card-title">Portfolio Distribution</h5>
              <Pie data={pieData} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
