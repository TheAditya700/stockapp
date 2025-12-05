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
  const [successMessage, setSuccessMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false); // Toggle between login and registration

  // Function to handle form submission (for login)
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      // Login request
      const loginResponse = await axios.post('/login', {
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
        const userResponse = await axios.get(`/user/${userId}`);
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
        setError('Login failed. Network error?');
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
    setSuccessMessage('');

    try {
      // Registration request
      const registerResponse = await axios.post('/register', {
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
        // Registration successful
        setIsRegistering(false); // Switch to login mode
        setSuccessMessage('Registration successful! Please login.');
        // Optionally clear sensitive fields but keep email for convenience
        setPassword('');
        setName('');
        setPhoneNumber('');
        setLocality('');
        setCity('');
        setBuilding('');
        setHno('');
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
    <div className="row w-100 h-100 g-0">
      {/* Left Side: Branding and Greeting */}
      <div className="col-md-6" style={{ padding: '10px 20px 20px 20px' }}>
        <div className="bg-primary text-white h-100 w-100 d-flex flex-column justify-content-center align-items-center" style={{ borderRadius: '15px' }}>
            <h1 className="display-3 fw-bold mb-3">StockStock</h1>
            <h3 className="fw-light">{isRegistering ? 'Hello there!' : 'Welcome back!'}</h3>
        </div>
      </div>

      {/* Right Side: Form */}
      <div className="col-md-6 d-flex justify-content-center align-items-center bg-white">
        <div className="login-container p-4">
          <h2 className="text-center mb-4">{isRegistering ? 'Register' : 'Login'}</h2>
          {error && <p className="text-danger text-center">{error}</p>}
          {successMessage && <p className="text-success text-center">{successMessage}</p>}
          
          <form onSubmit={isRegistering ? handleRegisterSubmit : handleLoginSubmit}>
            {isRegistering && (
              <>
                <div className="row">
                  <div className="col-md-6 form-group mb-3">
                    <label>Name:</label>
                    <input
                      type="text"
                      className="form-control"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      required
                    />
                  </div>

                  <div className="col-md-6 form-group mb-3">
                    <label>Phone Number:</label>
                    <input
                      type="text"
                      className="form-control"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="row">
                  <div className="col-md-6 form-group mb-3">
                    <label>Locality:</label>
                    <input
                      type="text"
                      className="form-control"
                      value={locality}
                      onChange={(e) => setLocality(e.target.value)}
                      required
                    />
                  </div>

                  <div className="col-md-6 form-group mb-3">
                    <label>City:</label>
                    <input
                      type="text"
                      className="form-control"
                      value={city}
                      onChange={(e) => setCity(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="row">
                  <div className="col-md-6 form-group mb-3">
                    <label>Building:</label>
                    <input
                      type="text"
                      className="form-control"
                      value={building}
                      onChange={(e) => setBuilding(e.target.value)}
                      required
                    />
                  </div>

                  <div className="col-md-6 form-group mb-3">
                    <label>House No:</label>
                    <input
                      type="text"
                      className="form-control"
                      value={hno}
                      onChange={(e) => setHno(e.target.value)}
                      required
                    />
                  </div>
                </div>
              </>
            )}

            <div className="form-group mb-3">
              <label>Email:</label>
              <input
                type="email"
                className="form-control"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="form-group mb-3">
              <label>Password:</label>
              <input
                type="password"
                className="form-control"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <div className="d-grid gap-2">
                <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? (isRegistering ? 'Registering...' : 'Logging in...') : (isRegistering ? 'Register' : 'Login')}
                </button>
            </div>
          </form>

          <div className="mt-3 text-center">
            <span>{isRegistering ? 'Already have an account?' : 'Don\'t have an account?'} </span>
                    <button
                      className="btn btn-link p-0 align-baseline text-primary"
                      onClick={() => setIsRegistering(!isRegistering)}>
                      {isRegistering ? 'Login here' : 'Register here'}
                    </button>          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
