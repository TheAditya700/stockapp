import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';

const AssetDetails = ({ asset, userData, onSwitchToWatchlist }) => {
  const [quantity, setQuantity] = useState('');
  const [orderType, setOrderType] = useState('Buy'); // Default to "Buy"
  const [price, setPrice] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [priceData, setPriceData] = useState([]); // State to hold historical price data
  const [watchlists, setWatchlists] = useState([]); // To store user's watchlists
  const [selectedWatchlist, setSelectedWatchlist] = useState(null); // Selected watchlist for adding the asset
  const [watchlistError, setWatchlistError] = useState(null); // Error message for watchlist addition

  // Fetch asset price, historical prices, and user's watchlists on load and interval
  useEffect(() => {
    if (!asset?.aid) return;

    const fetchAssetData = () => {
      // Fetch current price
      fetch(`/api/assets/${asset.aid}`)
        .then((res) => res.json())
        .then((data) => setPrice(data.price))
        .catch(() => setError('Could not fetch asset price.'));

      // Fetch historical prices
      fetch(`/api/assets/prices/${asset.aid}`)
        .then((res) => res.json())
        .then((data) => setPriceData(data))
        .catch(() => setError('Could not fetch historical price data.'));
    };

    // Fetch immediately
    fetchAssetData();
    
    // Fetch watchlists only once
    fetch(`/api/watchlists/${userData.uid}`)
      .then((res) => res.json())
      .then((data) => {
        setWatchlists(data);
        if (data.length > 0) {
          setSelectedWatchlist(data[0].wid);
        }
      })
      .catch(() => setWatchlistError('Could not fetch watchlists.'));

    // Set up interval for live updates (every 10 seconds)
    const intervalId = setInterval(fetchAssetData, 10000);

    // Cleanup on unmount
    return () => clearInterval(intervalId);

  }, [asset, userData]);

  // ... (Handle placing order and adding to watchlist - NO CHANGES HERE) ...

  // Handle placing an order
  const handlePlaceOrder = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    const qty = Number(quantity); // Ensure quantity is a number
    const totalCost = price * qty;

    if (qty <= 0) {
      setError('Please enter a valid quantity.');
      return;
    }
    if (qty > 50) {
      setError('Order quantity cannot exceed 50 stocks.');
      return;
    }
    if (totalCost > 100000) {
      setError('Transaction value cannot exceed ₹1,00,000.');
      return;
    }

    const orderData = {
      uid: userData.uid,
      aid: asset.aid,
      qty: qty,
      otype: orderType,
    };

    try {
      const response = await fetch('/api/place_order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to place order.');
      } else {
        setSuccess('Order placed successfully!');
      }
    } catch (error) {
      setError('Error placing order: ' + error.message);
    }
  };

  // Handle adding the asset to a watchlist
  const handleAddToWatchlist = () => {
    if (!selectedWatchlist) {
      setWatchlistError('Please select a watchlist.');
      return;
    }

    fetch(`/api/watchlists/${selectedWatchlist}/assets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ aid: asset.aid }),
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error('Failed to add asset to watchlist.');
        }
        return res.json();
      })
      .then(() => {
        if (onSwitchToWatchlist) {
          onSwitchToWatchlist(selectedWatchlist); // Notify parent to switch tabs
        }
        setSuccess('Asset added to watchlist successfully!');
      })
      .catch((err) => {
        setWatchlistError(err.message);
      });
  };

  // Prepare data for the Line chart
  const chartData = {
    labels: priceData.map((data) => {
        // Extract time only: "YYYY-MM-DD HH:mm:ss" -> "HH:mm:ss"
        const dateStr = data.date;
        return dateStr.length > 10 ? dateStr.substring(11) : dateStr;
    }),
    datasets: [
      {
        label: 'Close Price',
        data: priceData.map((data) => data.close_price),
        borderColor: '#55868c', // var(--dark-cyan)
        backgroundColor: 'rgba(85, 134, 140, 0.1)', // Light fill
        fill: true,
        pointRadius: 2,
        pointBackgroundColor: '#23001e', // var(--midnight-violet)
      },
    ],
  };

  if (!asset) {
    return <p>No asset selected.</p>;
  }

  return (
    <div className="asset-details">
      <h2>{asset.name}</h2>
      <p>Current Price: ₹{price !== null ? price : 'Loading...'}</p>
      {error && <p className="alert alert-danger">{error}</p>}
      {success && <p className="alert alert-success">{success}</p>}

      {/* Price Chart */}
      <div className="price-chart mb-4">
        <h3>Price History</h3>
        <Line data={chartData} />
      </div>

      {/* Form for placing orders */}
      <form onSubmit={handlePlaceOrder}>
        <div className="form-group">
          <label>Order Type</label>
          <select
            className="form-control"
            value={orderType}
            onChange={(e) => setOrderType(e.target.value)}
          >
            <option value="Buy">Buy</option>
            <option value="Sell">Sell</option>
          </select>
        </div>

        <div className="form-group">
          <label>Quantity</label>
          <input
            type="number"
            className="form-control"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            required
            max="50"
            min="1"
          />
        </div>

        <p>
          Total Cost: ₹
          {(price && quantity) ? (price * Number(quantity)).toFixed(2) : 0}
        </p>
        <button type="submit" className="btn btn-primary mt-3">
          Place Order
        </button>
      </form>

      {/* Add to Watchlist Section */}
      <div className="add-to-watchlist mt-4">
        <h4>Add to Watchlist</h4>
        {watchlistError && <p className="alert alert-danger">{watchlistError}</p>}
        <div className="form-group">
          <label>Select Watchlist</label>
          <select
            className="form-control"
            value={selectedWatchlist || ''}
            onChange={(e) => setSelectedWatchlist(e.target.value)}
          >
            {watchlists.map((watchlist) => (
              <option key={watchlist.wid} value={watchlist.wid}>
                {watchlist.wname}
              </option>
            ))}
          </select>
        </div>
        <button
          className="btn btn-primary mt-3"
          onClick={handleAddToWatchlist}
          disabled={!selectedWatchlist}
        >
          Add to Watchlist
        </button>
      </div>
    </div>
  );
};

export default AssetDetails;
