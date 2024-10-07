
const Dashboard = () => {
  return (
    <div className="dashboard">
      <h1>Hi, Aditya</h1>
      <div className="account-overview">
        <div>
          <h3>Equity</h3>
          <p>0</p>
          <small>Margin available: 0</small>
        </div>
        <div>
          <h3>Commodity</h3>
          <p>0</p>
          <small>Margin available: 0</small>
        </div>
      </div>
      <div className="market-overview">
        <h4>Market Overview</h4>
        <img src="graph.png" alt="Market Overview" />
      </div>
      <div className="investment-cta">
        <p>You don’t have any stocks in your DEMAT yet.</p>
        <button>Start investing</button>
      </div>
    </div>
  );
};

export default Dashboard;
