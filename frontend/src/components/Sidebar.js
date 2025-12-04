import React, { useState, useEffect } from 'react';

const Sidebar = ({ userData, onLogout, onSelectAsset }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  // Fetch assets based on search query or load initial assets
  useEffect(() => {
    const fetchAssets = async () => {
      try {
        const response = await fetch(`/api/assets/search?q=${searchQuery}`);
        const data = await response.json();
        setSearchResults(data);
      } catch (error) {
        console.error("Error fetching assets:", error);
      }
    };

    fetchAssets();
    const intervalId = setInterval(fetchAssets, 10000);
    return () => clearInterval(intervalId);
  }, [searchQuery]);

  // Handle asset selection
  const handleAssetClick = (asset) => {
    onSelectAsset(asset); // Pass the selected asset up to Dashboard
  };

  return (
    <div className="sidebar bg-light p-3 h-100 d-flex flex-column">
      {/* Search Input - Fixed at top */}
      <div className="flex-shrink-0">
        <input
          type="text"
          className="form-control mb-3"
          placeholder="Search for assets"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Search Results - Scrollable */}
      <div className="search-results flex-grow-1 overflow-auto">
        <ul className="list-group">
          {searchResults.map((result) => (
            <li
              key={result.aid}
              className="list-group-item d-flex justify-content-between"
              onClick={() => handleAssetClick(result)}
              style={{ cursor: 'pointer' }}
            >
              {result.name} <span>₹{result.price}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default Sidebar;
