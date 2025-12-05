import React, { useState, useEffect } from 'react';

const Orders = ({ userData }) => {
  const [pendingOrders, setPendingOrders] = useState([]);
  const [completedOrders, setCompletedOrders] = useState([]);

  // Fetch orders data for the specific user when the component mounts
  useEffect(() => {
    if (userData && userData.uid) { // Ensure userData and userData.uid are available
      fetch(`/api/orders/${userData.uid}`)
        .then((response) => response.json())
        .then((data) => {
          // Separate orders into pending and completed
          const pending = data.filter((order) => order.status === 'Pending');
          const completed = data.filter((order) => order.status === 'Completed');
          setPendingOrders(pending);
          setCompletedOrders(completed);
        })
        .catch((error) => console.error('Error fetching orders:', error));
    }
  }, [userData]); // Re-run if userData changes

  const handleDeleteOrder = async (orderId) => {
    if (window.confirm("Are you sure you want to delete this order?")) {
      try {
        const response = await fetch(`/api/orders/${orderId}`, { method: 'DELETE' });
        if (!response.ok) {
          throw new Error("Failed to delete the order");
        }
        setPendingOrders(pendingOrders.filter((order) => order.oid !== orderId));
      } catch (error) {
        console.error('Error deleting order:', error);
      }
    }
  };

  return (
    <div>
      <h2>Your Orders</h2>

      {/* Table for Pending Orders */}
      <div className="mb-4">
        <h3><span className="order-heading">Pending Orders</span></h3>
        <table className="table table-striped">
          <thead>
            <tr>
              <th>#</th>
              <th>Asset Name</th>
              <th>Type</th>
              <th>Quantity</th>
              <th>Price</th>
              <th>Status</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {pendingOrders.map((order, index) => (
              <tr key={order.oid}>
                <td>{index + 1}</td> {/* Row number */}
                <td>{order.asset_name}</td>
                <td>{order.otype}</td>
                <td>{order.qty}</td>
                <td>₹{order.price}</td>
                <td>{order.status}</td>
                <td>{new Date(order.date).toLocaleDateString()}</td>
                <td>
                  <button 
                    className="btn btn-danger btn-sm" 
                    onClick={() => handleDeleteOrder(order.oid)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {pendingOrders.length === 0 && <p>No pending orders found.</p>}
      </div>

      {/* Table for Completed Orders */}
      <div>
        <h3><span className="order-heading">Completed Orders</span></h3>
        <table className="table table-striped">
          <thead>
            <tr>
              <th>#</th>
              <th>Asset Name</th>
              <th>Type</th>
              <th>Quantity</th>
              <th>Price</th>
              <th>Status</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {completedOrders.map((order, index) => (
              <tr key={order.oid}>
                <td>{index + 1}</td> {/* Row number */}
                <td>{order.asset_name}</td>
                <td>{order.otype}</td>
                <td>{order.qty}</td>
                <td>₹{order.price}</td>
                <td>{order.status}</td>
                <td>{new Date(order.date).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {completedOrders.length === 0 && <p>No completed orders found.</p>}
      </div>
    </div>
  );
};

export default Orders;
