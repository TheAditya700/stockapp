import React, { useState, useEffect } from 'react';
import Home from './Home';
import Portfolio from './Portfolio';
import Watchlist from './Watchlist';
import Orders from './Orders';
import UserDetails from './UserDetails';
import AssetDetails from './AssetDetails';

const Dashboard = ({ userData, selectedAsset, setSelectedAsset }) => {
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
    { id: 'user', label: 'User', component: <UserDetails userData={userData} /> },
    { id: 'asset', label: 'Asset', component: <AssetDetails asset={selectedAsset} userData={userData} onSwitchToWatchlist={handleSwitchToWatchlist} /> },
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
      </ul>

      <div className="tab-content mt-4">
        {tabs.find((tab) => tab.id === activeTab)?.component || <p>Invalid tab</p>}
      </div>
    </div>
  );
};

export default Dashboard;
