import React, { useState } from 'react';
import '../App.css';
import './Sidebar.css';

const Sidebar = () => {
  const [selectedWatchlist, setSelectedWatchlist] = useState('Watchlist 1');
  const watchlists = ['Watchlist 1', 'Watchlist 2', 'Watchlist 3'];

  return (
    <div className="sidebar bg-light p-3">
      <input type="text" className="form-control mb-3" placeholder="Search for assets" />

      <div className="market-indices mb-3">
        <p>NIFTY 50: <span>24,795.75</span></p>
        <p>SENSEX: <span>81,050.00</span></p>
      </div>

      <div className="watchlist">
        <h3>{selectedWatchlist}</h3>
        <ul className="list-group">
          <li className="list-group-item d-flex justify-content-between">
            GOLDBEES <span>₹63.81</span>
          </li>
          <li className="list-group-item d-flex justify-content-between">
            NIFTYBEES <span>₹278.01</span>
          </li>
          <li className="list-group-item d-flex justify-content-between">
            HDFCBANK <span>₹1617.80</span>
          </li>
        </ul>
      </div>

      <div className="watchlist-switcher mt-3">
        <label htmlFor="watchlist-select">Switch Watchlist</label>
        <select
          id="watchlist-select"
          className="form-select mt-2"
          value={selectedWatchlist}
          onChange={(e) => setSelectedWatchlist(e.target.value)}
        >
          {watchlists.map((list, index) => (
            <option key={index} value={list}>
              {list}
            </option>
          ))}
        </select>
        <button className="btn btn-primary btn-block mt-3">+ Add Watchlist</button>
      </div>
    </div>
  );
};

export default Sidebar;
