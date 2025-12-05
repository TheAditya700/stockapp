import React, { useState, useEffect } from 'react';
import Home from './Home';
import Portfolio from './Portfolio';
import Watchlist from './Watchlist';
import Orders from './Orders';
import UserDetails from './UserDetails';
import AssetDetails from './AssetDetails';
import './Dashboard.css'; // Import custom styles for tabs and layout

const Dashboard = ({ userData, selectedAsset, setSelectedAsset, onLogout }) => {
  const [activeTab, setActiveTab] = useState('home');
  const [activeWatchlist, setActiveWatchlist] = useState(null);

  // Automatically switch to "Asset" tab when selectedAsset changes
  useEffect(() => {
    if (selectedAsset) {
      setActiveTab('asset');
    }
  }, [selectedAsset]);

  const handleOrder = (asset) => {
    setSelectedAsset(asset);
    setActiveTab('asset');
  };

  const handleSwitchToWatchlist = (watchlistId) => {
    setActiveWatchlist(watchlistId); // Set the active watchlist
    setActiveTab('watchlist'); // Switch to the watchlist tab
  };

  const tabs = [
    { id: 'home', label: 'Home', component: <Home userData={userData} /> },
    { id: 'portfolio', label: 'Portfolio', component: <Portfolio userData={userData} onOrder={handleOrder} /> },
    { id: 'watchlist', label: 'Watchlist', component: <Watchlist userData={userData} activeWatchlist={activeWatchlist} /> },
    { id: 'orders', label: 'Orders', component: <Orders userData={userData} /> },
    { id: 'asset', label: 'Asset', component: <AssetDetails asset={selectedAsset} userData={userData} onSwitchToWatchlist={handleSwitchToWatchlist} /> },
    { id: 'user', label: 'User', component: <UserDetails userData={userData} /> },
  ];

  return (
    <div className="container-fluid">
      <ul className="nav nav-tabs">
        {tabs.map((tab) => (
          <li className="nav-item" key={tab.id}>
            <button
              className={`nav-link ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          </li>
        ))}
        <li className="nav-item ms-auto"> {/* ms-auto pushes this to the right */}
          <button className="btn btn-danger btn-sm" onClick={onLogout}>
            Logout
          </button>
        </li>
      </ul>

      <div className="tab-content mt-4">
        {tabs.find((tab) => tab.id === activeTab)?.component || <p>Invalid tab</p>}
      </div>
    </div>
  );
};

export default Dashboard;
