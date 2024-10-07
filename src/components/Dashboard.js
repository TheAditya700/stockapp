import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale, // The "category" scale
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

// Register the components manually for Chart.js v3+
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard = () => {
  // Dummy data for the graph
  const data = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
    datasets: [
      {
        label: 'NIFTY 50',
        data: [50, 60, 55, 70, 60, 75, 80, 85, 90, 85],
        fill: false,
        backgroundColor: '#007bff',
        borderColor: '#007bff',
      },
    ],
  };

  return (
    <div className="dashboard">
      <h1>Hi, Aditya</h1>
      <div className="row mt-4">
        {/* Equity Section */}
        <div className="col-md-6 mb-3">
          <div className="card text-center">
            <div className="card-body">
              <h5 className="card-title">Equity</h5>
              <h2>0</h2>
              <p>Margin available</p>
              <p>Margins used <span>0</span></p>
              <p>Opening balance <span>0</span></p>
              <a href="#" className="card-link">View statement</a>
            </div>
          </div>
        </div>

        {/* Commodity Section */}
        <div className="col-md-6 mb-3">
          <div className="card text-center">
            <div className="card-body">
              <h5 className="card-title">Commodity</h5>
              <h2>0</h2>
              <p>Margin available</p>
              <p>Margins used <span>0</span></p>
              <p>Opening balance <span>0</span></p>
              <a href="#" className="card-link">View statement</a>
            </div>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="text-center mb-5">
        <p>You don't have any stocks in your DEMAT yet. Get started with absolutely free equity investments.</p>
        <button className="btn btn-primary">Start investing</button>
      </div>

      {/* Market Overview */}
      <div className="market-overview">
        <h4>Market Overview</h4>
        <Line data={data} />
      </div>

      {/* Positions */}
      <div className="text-center mt-5">
        <p>You don’t have any positions yet</p>
        <button className="btn btn-primary">Get started</button>
      </div>
    </div>
  );
};

export default Dashboard;
