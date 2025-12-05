import React, { useEffect, useState, useCallback } from 'react';
import { Pie, Line } from 'react-chartjs-2';
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
  const [portfolioHistory, setPortfolioHistory] = useState([]);

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

  const fetchData = useCallback(() => {
    if (userData && userData.uid) {
      // removed setLoading(true) to avoid flickering on updates
      fetch(`/api/user/${userData.uid}/funds_status`)
        .then((res) => res.json())
        .then((data) => {
          const { available_margin_equity, available_margin_commodity, utilized_margin_equity, utilized_margin_commodity } = data;

          setAvailableMarginEquity(available_margin_equity);
          setAvailableMarginCommodity(available_margin_commodity);
          setUtilizedMarginEquity(utilized_margin_equity); // Set utilized margin for equity
          setUtilizedMarginCommodity(utilized_margin_commodity); // Set utilized margin for commodity

          // Fetch the total portfolio value
          fetch(`/api/user/${userData.uid}/portfolio_value`)
            .then((res) => res.json())
            .then((data) => {
              setPortfolioValue(data.total_portfolio_value || 0);
            })
            .catch((error) => {
              console.error('Error fetching portfolio value:', error);
            });

          // Fetch the total portfolio profit and profit percentage
          fetch(`/api/portfolio/summary/${userData.uid}`)
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
      fetch(`/api/user/${userData.uid}/total_values`)
        .then((res) => res.json())
        .then((data) => {
          setTotalEquityValue(data.total_equity_value || 0);
          setTotalCommodityValue(data.total_commodity_value || 0);
        })
        .catch((error) => {
          console.error('Error fetching total values:', error);
        });

      // Fetch portfolio history
      fetch(`/api/user/${userData.uid}/portfolio_history`)
        .then((res) => res.json())
        .then((data) => {
            setPortfolioHistory(data);
        })
        .catch((error) => {
            console.error('Error fetching portfolio history:', error);
        });
    }
  }, [userData]);

  // Fetch data when component mounts and every 10 seconds
  useEffect(() => {
    fetchData();
    const intervalId = setInterval(fetchData, 10000);
    return () => clearInterval(intervalId);
  }, [userData, fetchData]);

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
  }, [userData, fetchData]);

  const pieData = {
    labels: ['Equity', 'Commodity'],
    datasets: [
      {
        data: [totalEquityValue, totalCommodityValue], // Use total equity and commodity values here
        backgroundColor: ['#55868c', '#704e2e'], // Dark Cyan (Equity), Coffee Bean (Commodity)
        hoverBackgroundColor: ['#3d6064', '#5a3e25']
      }
    ]
  };

  const lineChartData = {
    labels: portfolioHistory.map(item => {
        const date = new Date(item.date);
        // Format time as HH:mm for intraday data
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }),
    datasets: [
      {
        label: 'Portfolio Value',
        data: portfolioHistory.map(item => item.value),
        fill: true,
        backgroundColor: 'rgba(85, 134, 140, 0.2)', // Light Dark Cyan
        borderColor: '#55868c', // Dark Cyan
        tension: 0.4, // Smooth curve
        pointRadius: 0, // Hide points for smoother look on high-density data
        hoverPointRadius: 4,
        pointBackgroundColor: '#23001e', // Midnight Violet
      },
    ],
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container my-4">
      <h1 className="mb-4">Hi, {userName}</h1>

      {/* Row 1: Total Portfolio Value (Full Width) */}
      <div className="row mb-4">
        <div className="col-md-12 mb-4 h-100">
          <div className="card text-center h-100">
            <div className="card-body d-flex flex-column justify-content-center align-items-center">
              <h6 className="card-title text-uppercase text-muted mb-3">Total Portfolio Value</h6>
              <h2 className="mb-3" style={{ fontSize: '2.5rem' }}>{formatNumber(portfolioValue)}</h2>
              <div className="d-flex gap-4">
                <p className="mb-0 fs-5">Total Profit: <span style={{ 
                  color: 'var(--midnight-violet)', 
                  backgroundColor: totalProfit >= 0 ? 'var(--celadon)' : 'var(--cotton-rose)',
                  padding: '4px 12px',
                  borderRadius: '20px',
                  fontWeight: 'bold'
                }}>{formatNumber(totalProfit)}</span></p>
                <p className="mb-0 fs-5">Return: <span className="fw-bold">{profitPercentage}%</span></p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Row 2: Charts (History & Distribution) */}
      <div className="row mb-4">
        <div className="col-md-6 mb-4">
          <div className="card text-center h-100">
            <div className="card-body">
              <h6 className="card-title text-uppercase text-muted mb-3">Value of Current Holdings</h6>
              <div style={{ height: '300px', width: '100%' }}>
                <Line 
                    data={lineChartData} 
                    options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { 
                                grid: { display: false },
                                ticks: { maxTicksLimit: 6 } // Limit x-axis labels to avoid crowding
                            },
                            y: { beginAtZero: false } 
                        }
                    }} 
                />
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-6 mb-4">
          <div className="card text-center h-100">
            <div className="card-body d-flex flex-column justify-content-center align-items-center">
              <h6 className="card-title text-uppercase text-muted mb-3">Portfolio Distribution</h6>
              <div style={{hieght: '300px', margin: '0 auto' }}>
                <Pie data={pieData} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Row 3: Equity and Commodity Stats */}
      <div className="row mb-4">
        <div className="col-md-6 mb-4">
          <div className="card text-center h-100">
            <div className="card-body">
              <h6 className="card-title text-uppercase text-muted mb-2">Equity</h6>
              <h3>{formatNumber(availableMarginEquity)}</h3>
              <p className="small text-muted mb-1">Margin Available</p>
              <p className="mb-1">Funds: {formatNumber(equity)}</p>
              <p className="mb-0">Utilized: {formatNumber(utilizedMarginEquity)}</p>
            </div>
          </div>
        </div>

        <div className="col-md-6 mb-4">
          <div className="card text-center h-100">
            <div className="card-body">
              <h6 className="card-title text-uppercase text-muted mb-2">Commodity</h6>
              <h3>{formatNumber(availableMarginCommodity)}</h3>
              <p className="small text-muted mb-1">Margin Available</p>
              <p className="mb-1">Funds: {formatNumber(commodity)}</p>
              <p className="mb-0">Utilized: {formatNumber(utilizedMarginCommodity)}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
