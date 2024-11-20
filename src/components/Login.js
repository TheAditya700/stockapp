import axios from 'axios';
import React, { useState } from 'react';

function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState(''); // For registration
  const [phoneNumber, setPhoneNumber] = useState(''); // For phone number
  const [locality, setLocality] = useState(''); // For address locality
  const [city, setCity] = useState(''); // For address city
  const [building, setBuilding] = useState(''); // For address building
  const [hno, setHno] = useState(''); // For address house number
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false); // Toggle between login and registration

  // Function to handle form submission (for login)
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Login request
      const loginResponse = await axios.post('http://localhost:5000/login', {
        uemail: email,
        password: password
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      // Check for successful login response
      if (loginResponse.status === 200) {
        const userId = loginResponse.data.user.uid; // Get the user ID

        // Fetch full user data with the user ID
        const userResponse = await axios.get(`http://localhost:5000/user/${userId}`);
        onLogin(userResponse.data);
      } else {
        setError('Invalid credentials');
      }
    } catch (err) {
      if (err.response) {
        if (err.response.status === 401) {
          setError('Invalid credentials');
        } else if (err.response.status === 404) {
          setError('User not found');
        } else {
          setError('An error occurred. Please try again.');
        }
      } else {
        setError('Registered Successfully.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Function to handle form submission (for registration)
  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Registration request
      const registerResponse = await axios.post('http://localhost:5000/register', {
        uname: name,
        uemail: email,
        password: password,
        upno: phoneNumber,  // Include phone number
        address: {
          locality: locality, // Send locality
          city: city,         // Send city
          building: building, // Send building
          hno: hno            // Send house number
        }
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (registerResponse.status === 201) {
        // Optionally, auto-login after successful registration
        const userId = registerResponse.data.user.uid; // Get the user ID
        const userResponse = await axios.get(`http://localhost:5000/user/${userId}`);
        onLogin(userResponse.data);
      } else {
        setError('Registration failed. Please try again.');
      }
    } catch (err) {
      if (err.response) {
        setError('An error occurred during registration. Please try again.');
      } else {
        setError('Network error. Please check your connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h2>{isRegistering ? 'Register' : 'Login'}</h2>
      {error && <p className="text-danger">{error}</p>}
      
      <form onSubmit={isRegistering ? handleRegisterSubmit : handleLoginSubmit}>
        {isRegistering && (
          <>
            <div className="form-group">
              <label>Name:</label>
              <input
                type="text"
                className="form-control"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>Phone Number:</label>
              <input
                type="text"
                className="form-control"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>Locality:</label>
              <input
                type="text"
                className="form-control"
                value={locality}
                onChange={(e) => setLocality(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>City:</label>
              <input
                type="text"
                className="form-control"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>Building:</label>
              <input
                type="text"
                className="form-control"
                value={building}
                onChange={(e) => setBuilding(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>House Number:</label>
              <input
                type="text"
                className="form-control"
                value={hno}
                onChange={(e) => setHno(e.target.value)}
                required
              />
            </div>
          </>
        )}

        <div className="form-group">
          <label>Email:</label>
          <input
            type="email"
            className="form-control"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label>Password:</label>
          <input
            type="password"
            className="form-control"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? (isRegistering ? 'Registering...' : 'Logging in...') : (isRegistering ? 'Register' : 'Login')}
        </button>
      </form>

      <div className="mt-3">
        <span>{isRegistering ? 'Already have an account?' : 'Don\'t have an account?'} </span>
        <button 
          className="btn btn-link" 
          onClick={() => setIsRegistering(!isRegistering)}>
          {isRegistering ? 'Login here' : 'Register here'}
        </button>
      </div>
    </div>
  );
}

export default Login;
