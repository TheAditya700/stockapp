import React, { useEffect, useState, useCallback } from 'react';

const Portfolio = ({ userData, onOrder }) => {
  const [portfolioData, setPortfolioData] = useState([]);
  const [totalProfit, setTotalProfit] = useState(0);
  const [totalProfitPercentage, setTotalProfitPercentage] = useState(0);

  // Function to calculate profit and profit percentage
  const calculateProfit = (buyPrice, currentPrice, qty) => {
    if (buyPrice === null || currentPrice === null) return { profit: 'N/A', profitPercentage: 'N/A', profitStyle: {}, profitPercentageStyle: {} };

    // In case of short-selling (negative qty), reverse the profit/loss logic
    const profit = qty < 0
      ? (buyPrice - currentPrice) * Math.abs(qty) // Negative quantity means selling, calculate profit accordingly
      : (currentPrice - buyPrice) * qty; // Positive quantity means buying, calculate normally

    const profitPercentage = qty < 0
      ? ((buyPrice - currentPrice) / buyPrice) * 100  // For short selling
      : ((currentPrice - buyPrice) / buyPrice) * 100; // For regular buying

    // Determine the style based on whether it's a profit, loss, or zero
    const profitStyle = profit > 0 ? { color: 'green', fontWeight: 'bold' }
      : profit < 0 ? { color: 'red', fontWeight: 'bold' }
      : { color: 'grey', fontWeight: 'bold' }; // Grey for zero profit

    const profitPercentageStyle = profitPercentage > 0 ? { color: 'green', fontWeight: 'bold' }
      : profitPercentage < 0 ? { color: 'red', fontWeight: 'bold' }
      : { color: 'grey', fontWeight: 'bold' }; // Grey for zero percentage

    return {
      profit: profit.toFixed(2),
      profitPercentage: profitPercentage.toFixed(2),
      profitStyle: profitStyle,
      profitPercentageStyle: profitPercentageStyle,
    };
  };

  // Function to calculate total profit and total profit percentage for the entire portfolio
  const calculateTotalProfitAndPercentage = useCallback((data) => {
    let totalProfitSum = 0;
    let totalInvestment = 0;
    data.forEach((holding) => {
      if (holding.buy_price && holding.current_price && holding.qty) {
        const { profit } = calculateProfit(holding.buy_price, holding.current_price, holding.qty);
        totalProfitSum += parseFloat(profit);
        totalInvestment += holding.buy_price * holding.qty;
      }
    });
    const totalProfitPercent = totalInvestment ? (totalProfitSum / totalInvestment) * 100 : 0;
    setTotalProfit(totalProfitSum.toFixed(2));
    setTotalProfitPercentage(totalProfitPercent.toFixed(2));
  }, [setTotalProfit, setTotalProfitPercentage]);

  useEffect(() => {
    if (userData && userData.uid) {
      fetch(`/api/portfolio/${userData.uid}`)
        .then((response) => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then((data) => {
          setPortfolioData(data);
          calculateTotalProfitAndPercentage(data);
        })
        .catch((error) => console.error('Error fetching portfolio data:', error));
    }
  }, [userData, calculateTotalProfitAndPercentage]);

  return (
    <div className="portfolio">
      <h2>Your Portfolio</h2>
      {portfolioData.length === 0 ? (
        <p>Your Portfolio is empty.</p>
      ) : (
        <table className="table table-striped">
          <thead>
            <tr>
              <th>Asset</th>
              <th>Quantity</th>
              <th>Buy Price</th>
              <th>Current Price</th>
              <th>Total Value</th>
              <th>Profit</th>
              <th>Profit (%)</th>
            </tr>
          </thead>
          <tbody>
            {portfolioData.map((holding, index) => {
              const { profit, profitPercentage, profitStyle, profitPercentageStyle } = calculateProfit(
                holding.buy_price,
                holding.current_price,
                holding.qty
              );

              return (
                <tr key={index}>
                  <td>{holding.asset_name}</td>
                  <td>{holding.qty}</td>
                  <td>{holding.buy_price ? `₹${holding.buy_price}` : 'N/A'}</td>
                  <td>{holding.current_price ? `₹${holding.current_price}` : 'N/A'}</td>
                  <td>₹{holding.total_value}</td>
                  <td style={profitStyle}>{profit}</td> {/* Apply the profit style */}
                  <td style={profitPercentageStyle}>{profitPercentage}%</td> {/* Apply the profit percentage style */}
                </tr>
              );
            })}
          </tbody>
          <tfoot>
            <tr>
              <td colSpan="5" className="text-end">Total Profit</td>
              <td>₹{totalProfit}</td>
              <td>{totalProfitPercentage}%</td>
            </tr>
          </tfoot>
        </table>
      )}
    </div>
  );
};

export default Portfolio;
