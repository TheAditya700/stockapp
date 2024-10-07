import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Orders from './components/Orders';
import Holdings from './components/Holdings';
import 'bootstrap/dist/css/bootstrap.min.css'; // Import Bootstrap

function App() {
  return (
    <Router>
      <div className="container-fluid">
        <div className="row">
          {/* Sidebar takes 3 columns */}
          <div className="col-md-3">
            <Sidebar />
          </div>

          {/* Main content takes 9 columns */}
          <div className="col-md-9">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/orders" element={<Orders />} />
              <Route path="/holdings" element={<Holdings />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
}

export default App;
