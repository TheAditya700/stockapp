import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import Header from './components/Header';
import Footer from './components/Footer';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

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
    <div className="d-flex flex-column vh-100 overflow-hidden">
      <Header />
      
      <div className="container-fluid flex-grow-1 d-flex flex-column overflow-hidden">
        {!isAuthenticated ? (
          <div className="d-flex justify-content-center align-items-center h-100">
             <Login onLogin={handleLogin} />
          </div>
        ) : (
          <div className="row flex-grow-1 overflow-hidden">
            <div className="col-md-3 border-end sidebar-panel p-0">
              <Sidebar
                userData={userData}
                onLogout={handleLogout}
                onSelectAsset={setSelectedAsset}
              />
            </div>
            <div className="col-md-9 h-100 overflow-auto p-4">
              <Dashboard
                userData={userData}
                selectedAsset={selectedAsset}
                setSelectedAsset={setSelectedAsset}
              />
            </div>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
}

export default App;
