import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Orders from './components/Orders';
import Holdings from './components/Holdings';

function App() {
  return (
    <Router>
      <div className="App">
        <Sidebar />
        <div className="main-content">
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/holdings" element={<Holdings />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
