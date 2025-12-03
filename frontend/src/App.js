import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userData, setUserData] = useState(null);
  const [selectedAsset, setSelectedAsset] = useState(null);

  const handleLogin = (user) => {
    setIsAuthenticated(true);
    setUserData(user);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setUserData(null);
  };

  return (
    <div className="container-fluid">
      {!isAuthenticated ? (
        <Login onLogin={handleLogin} />
      ) : (
        <div className="row">
          <div className="col-md-3">
            <Sidebar
              userData={userData}
              onLogout={handleLogout}
              onSelectAsset={setSelectedAsset}
            />
          </div>
          <div className="col-md-9">
            <Dashboard
              userData={userData}
              selectedAsset={selectedAsset}
              setSelectedAsset={setSelectedAsset}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
