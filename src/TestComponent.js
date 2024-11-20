// TestComponent.js
import React, { useContext } from 'react';
import { AuthContext } from './context/AuthContext';

const TestComponent = () => {
  const { isAuthenticated, login, logout } = useContext(AuthContext);

  console.log('AuthContext in TestComponent:', { isAuthenticated, login, logout });

  return <div>Test if AuthContext is working</div>;
};

export default TestComponent;
