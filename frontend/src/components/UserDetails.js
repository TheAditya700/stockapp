import React, { useState, useEffect } from 'react';

const UserDetails = ({ userData }) => {
  const userId = userData?.uid;

  const [userDetails, setUserDetails] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [newAddress, setNewAddress] = useState({ hno: '', locality: '', city: '', building: '' });
  const [paymentMode, setPaymentMode] = useState('UPI');
  const [fundsAction, setFundsAction] = useState('add');
  const [fundsType, setFundsType] = useState('equity');
  const [fundsAmount, setFundsAmount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [password, setPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  useEffect(() => {
    if (!userId) return;

    const fetchUserData = async () => {
      try {
        const userResponse = await fetch(`http://127.0.0.1:5000/user/${userId}`);
        if (!userResponse.ok) throw new Error('Failed to fetch user data');
        const userData = await userResponse.json();
        setUserDetails(userData);

        const addressResponse = await fetch(`http://127.0.0.1:5000/user/${userId}/addresses`);
        if (!addressResponse.ok) throw new Error('Failed to fetch addresses');
        const addressData = await addressResponse.json();
        setAddresses(addressData);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [userId]);

  const handleLogout = () => {
    // Remove user session data (if stored in localStorage or cookies)
    localStorage.removeItem('userData'); // or cookies.remove('userData')
    // Refresh the page
    window.location.reload();
  };

  const handleFundsAction = async () => {
    if (fundsAmount <= 0) {
      alert('Enter a valid amount');
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:5000/user/${userId}/funds`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: fundsType,
          action: fundsAction,
          amount: fundsAmount,
          payment_mode: paymentMode,
        }),
      });

      if (!response.ok) throw new Error('Failed to update funds');

      const updatedFunds = await response.json();
      setUserDetails((prev) => ({
        ...prev,
        equity_funds: updatedFunds.equity_funds,
        commodity_funds: updatedFunds.commodity_funds,
      }));

      alert('Funds updated successfully');
    } catch (error) {
      setError(error.message);
    }
  };

  const handleAddAddress = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/user/${userId}/addresses`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newAddress),
      });

      if (!response.ok) throw new Error('Failed to add address');
      const addedAddress = await response.json();
      setAddresses([...addresses, addedAddress]);
      setNewAddress({ hno: '', locality: '', city: '', building: '' });
    } catch (error) {
      setError(error.message);
    }
  };

  const handleRemoveAddress = async (addressId) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/user/${userId}/addresses/${addressId}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to remove address');
      setAddresses(addresses.filter((addr) => addr.address_id !== addressId));
    } catch (error) {
      setError(error.message);
    }
  };

  const handlePasswordUpdate = async () => {
    if (newPassword !== confirmPassword) {
      alert('Passwords do not match');
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:5000/user/${userId}/password`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_password: password, new_password: newPassword }),
      });

      if (!response.ok) throw new Error('Failed to update password');
      alert('Password updated successfully');
      setPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (error) {
      alert('Error updating password: ' + error.message);
    }
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p className="text-danger">Error: {error}</p>;

  return (
    <div className="container py-4">
      <h2 className="mb-4">User Details</h2>
      {userDetails && (
        <div className="card p-3 mb-4">
          <h5 className="card-title">{userDetails.uname}</h5>
          <p className="card-text"><strong>Email:</strong> {userDetails.uemail}</p>
          <p className="card-text"><strong>Equity Funds:</strong> ₹{userDetails.equity_funds}</p>
          <p className="card-text"><strong>Commodity Funds:</strong> ₹{userDetails.commodity_funds}</p>
        </div>
      )}

      <h3>Manage Funds</h3>
      <div className="card p-3 mb-4">
        <div className="d-flex mb-3">
          <select
            className="form-select me-2"
            value={fundsAction}
            onChange={(e) => setFundsAction(e.target.value)}
          >
            <option value="add">Add Funds</option>
            <option value="withdraw">Withdraw Funds</option>
          </select>
          <select
            className="form-select me-2"
            value={fundsType}
            onChange={(e) => setFundsType(e.target.value)}
          >
            <option value="equity">Equity</option>
            <option value="commodity">Commodity</option>
          </select>
          <input
            type="number"
            className="form-control me-2"
            placeholder="Amount"
            value={fundsAmount}
            onChange={(e) => setFundsAmount(e.target.value)}
          />
          <select
            className="form-select me-2"
            value={paymentMode}
            onChange={(e) => setPaymentMode(e.target.value)}
          >
            <option value="UPI">UPI</option>
            <option value="Card">Card</option>
          </select>
          <button className="btn btn-primary" onClick={handleFundsAction}>Submit</button>
        </div>
      </div>

      <h3>Manage Addresses</h3>
      <div className="mb-4">
        <ul className="list-group mb-3">
          {addresses.map((address) => (
            <li className="list-group-item d-flex justify-content-between align-items-center" key={address.address_id}>
              <span>
                <strong>House No:</strong> {address.hno}, <strong>Locality:</strong> {address.locality}, <strong>City:</strong> {address.city}, <strong>Building:</strong> {address.building}
              </span>
              <button className="btn btn-danger btn-sm" onClick={() => handleRemoveAddress(address.address_id)}>Remove</button>
            </li>
          ))}
        </ul>
        <div className="card p-3">
          <h5>Add New Address</h5>
          <div className="row g-2">
            <div className="col-md-3">
              <input
                type="text"
                className="form-control"
                placeholder="House No"
                value={newAddress.hno}
                onChange={(e) => setNewAddress({ ...newAddress, hno: e.target.value })}
              />
            </div>
            <div className="col-md-3">
              <input
                type="text"
                className="form-control"
                placeholder="Locality"
                value={newAddress.locality}
                onChange={(e) => setNewAddress({ ...newAddress, locality: e.target.value })}
              />
            </div>
            <div className="col-md-3">
              <input
                type="text"
                className="form-control"
                placeholder="City"
                value={newAddress.city}
                onChange={(e) => setNewAddress({ ...newAddress, city: e.target.value })}
              />
            </div>
            <div className="col-md-3">
              <input
                type="text"
                className="form-control"
                placeholder="Building"
                value={newAddress.building}
                onChange={(e) => setNewAddress({ ...newAddress, building: e.target.value })}
              />
            </div>
          </div>
          <button className="btn btn-primary mt-3" onClick={handleAddAddress}>Add Address</button>
        </div>
      </div>

      <h3>Change Password</h3>
      <div className="card p-3 mb-4">
        <input
          type="password"
          className="form-control mb-2"
          placeholder="Current Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <input
          type="password"
          className="form-control mb-2"
          placeholder="New Password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
        />
        <input
          type="password"
          className="form-control mb-2"
          placeholder="Confirm New Password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
        />
        <button className="btn btn-primary" onClick={handlePasswordUpdate}>Update Password</button>
      </div>
      <button className="btn btn-danger" onClick={handleLogout}>Logout</button>
    </div>
  );
};

export default UserDetails;
 