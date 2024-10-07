
const Sidebar = () => {
  return (
    <div className="sidebar">
      <input type="text" placeholder="Search for assets" />
      <div className="market-indices">
        <p>NIFTY 50: <span>24795.75</span></p>
        <p>SENSEX: <span>81050.00</span></p>
      </div>
      <div className="watchlist">
        <h3>Watchlist</h3>
        <ul>
          <li>GOLDBEES <span>63.81</span></li>
          <li>NIFTYBEES <span>278.01</span></li>
          <li>HDFCBANK <span>1617.80</span></li>
        </ul>
      </div>
    </div>
  );
};

export default Sidebar;
