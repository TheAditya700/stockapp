import React, { useEffect, useState, useCallback } from 'react';

const Watchlist = ({ userData, activeWatchlist }) => {
  const [watchlists, setWatchlists] = useState([]); // Store the fetched watchlists
  const [selectedWatchlist, setSelectedWatchlist] = useState(null); // Currently selected watchlist
  const [watchlistAssets, setWatchlistAssets] = useState([]); // Assets of the selected watchlist
  const [newWatchlistName, setNewWatchlistName] = useState(''); // Name for a new watchlist
  const [isAdding, setIsAdding] = useState(false); // Toggle for adding a new watchlist

  // Fetch watchlists from API
  const fetchWatchlists = useCallback(() => {
    if (userData && userData.uid) {
      fetch(`/api/watchlists/${userData.uid}`) // Fetch user-specific watchlists
        .then((response) => response.json())
        .then((data) => {
          setWatchlists(data);

          // Set selectedWatchlist to activeWatchlist or the first available watchlist
          if (data.length > 0) {
            setSelectedWatchlist(activeWatchlist || data[0].wid);
          }
        })
        .catch((error) => console.error('Error fetching watchlists:', error));
    }
  }, [userData, activeWatchlist, setSelectedWatchlist, setWatchlists]);

  useEffect(() => {
    fetchWatchlists();
  }, [userData, activeWatchlist, fetchWatchlists]); // Listen to changes in userData or activeWatchlist

  // Fetch assets of the selected watchlist
  const fetchAssets = useCallback(() => {
    if (selectedWatchlist) {
      fetch(`/api/watchlists/${selectedWatchlist}/assets`)
        .then((response) => response.json())
        .then((data) => setWatchlistAssets(data))
        .catch((error) => console.error('Error fetching watchlist assets:', error));
    }
  }, [selectedWatchlist, setWatchlistAssets]);

  useEffect(() => {
    fetchAssets();
  }, [selectedWatchlist, fetchAssets]);

  // Add a new watchlist
  const handleAddWatchlist = () => {
    if (newWatchlistName && userData) {
      fetch(`/api/watchlists`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newWatchlistName, uid: userData.uid }),
      })
        .then((response) => response.json())
        .then((data) => {
          fetchWatchlists(); // Refresh the watchlist tabs
          setSelectedWatchlist(data.wid); // Automatically select the new watchlist
          setNewWatchlistName(''); // Reset the input field
          setIsAdding(false); // Exit add mode
        })
        .catch((error) => console.error('Error creating new watchlist:', error));
    }
  };

  // Remove an asset from the watchlist
  const handleRemoveAsset = (aid) => {
    fetch(`/api/watchlists/${selectedWatchlist}/assets/${aid}`, {
      method: 'DELETE',
    })
      .then((response) => {
        if (response.ok) {
          fetchAssets(); // Refresh assets after removal
        } else {
          throw new Error('Failed to remove asset');
        }
      })
      .catch((error) => console.error('Error removing asset:', error));
  };

  // Delete the selected watchlist
  const handleDeleteWatchlist = () => {
    if (window.confirm('Are you sure you want to delete this watchlist?')) {
      fetch(`/api/watchlists/${selectedWatchlist}`, {
        method: 'DELETE',
      })
        .then((response) => {
          if (response.ok) {
            fetchWatchlists(); // Refresh the watchlists after deletion
            setSelectedWatchlist(null); // Clear the selected watchlist
          } else {
            throw new Error('Failed to delete watchlist');
          }
        })
        .catch((error) => console.error('Error deleting watchlist:', error));
    }
  };

  // Handle form submission for new watchlist
  const handleNewWatchlistSubmit = (e) => {
    e.preventDefault();
    handleAddWatchlist();
  };

  return (
    <div className="container-fluid">
      {/* Tabs for watchlists */}
      <ul className="nav nav-tabs">
        {watchlists.map((watchlist) => (
          <li className="nav-item" key={watchlist.wid}>
            <button
              className={`nav-link ${selectedWatchlist === watchlist.wid ? 'active' : ''}`}
              onClick={() => setSelectedWatchlist(watchlist.wid)}
            >
              {watchlist.wname}
            </button>
          </li>
        ))}
        {/* Inline Form for Adding Watchlist */}
        <li className="nav-item">
          {isAdding ? (
            <form onSubmit={handleNewWatchlistSubmit} className="d-flex align-items-center">
              <input
                type="text"
                className="form-control"
                placeholder="Enter Watchlist Name"
                value={newWatchlistName}
                onChange={(e) => setNewWatchlistName(e.target.value)}
                autoFocus
              />
              <button
                type="button"
                className="btn btn-secondary ms-2"
                onClick={() => {
                  setIsAdding(false);
                  setNewWatchlistName('');
                }}
              >
                Cancel
              </button>
            </form>
          ) : (
            <button className="nav-link" onClick={() => setIsAdding(true)}>
              + Add Watchlist
            </button>
          )}
        </li>
      </ul>

      {/* Watchlist Assets Table */}
      <div className="mt-4">
        {watchlistAssets.length > 0 ? (
          <table className="table table-bordered">
            <thead>
              <tr>
                <th>Asset Name</th>
                <th>Current Price</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {watchlistAssets.map((asset) => (
                <tr key={asset.aid}>
                  <td>{asset.name}</td>
                  <td>{asset.current_price}</td>
                  <td>
                    <button
                      className="btn btn-danger"
                      onClick={() => handleRemoveAsset(asset.aid)}
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No assets in this watchlist.</p>
        )}
      </div>

      {/* Delete Watchlist Button */}
      <div className="mt-3">
        <button
          className="btn btn-danger"
          onClick={handleDeleteWatchlist}
          disabled={!selectedWatchlist} // Disable if no watchlist is selected
        >
          Delete Watchlist
        </button>
      </div>
    </div>
  );
};

export default Watchlist;
