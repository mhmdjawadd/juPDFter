import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import FileUpload from './components/FileUpload';
import ProgressIndicator from './components/ProgressIndicator';
import DownloadList from './components/DownloadList';
import LoginSignup from './pages/loginSignUp';
import PremiumPlans from './pages/PremiumPlans'; // Import the PremiumPlans component
import axios from 'axios'; // Import Axios for API calls
import { Link } from 'react-router-dom'; // Use Link instead of useNavigate

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false); // Track login status

  // Logout function
  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        'http://localhost:5000/logout', 
        {}, 
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      if (response.data.status === 'success') {
        localStorage.removeItem("token");
        setIsAuthenticated(false); // Update authentication state

      } else {
        alert(response.data.message);
      }
    } catch (error) {
      console.error('Error during logout:', error);
      alert('Logout failed.');
    }
  };

  return (
    <Router>
      <Routes>
        {/* Login/Signup Page */}
            <Route
                  path="/"
                  element={
                    isAuthenticated ? (
                      <>
                        {console.log("Redirecting to dashboard...")}
                        <Navigate to="/dashboard" replace />
                      </>
                    ) : (
                      <LoginSignup setIsAuthenticated={setIsAuthenticated} />
                    )
                  }
                />

        {/* Dashboard Page */}
        <Route
          path="/dashboard"
          element={
            isAuthenticated ? (
              <div className="App">
                <button onClick={handleLogout} className="btn logout-button">
                  Logout
                </button>
                {/* Premium Plans Button */}
                <Link to="/premium-plans" className="btn premium-button">
                  Premium Plans
                </Link>
                <FileUpload />
                <ProgressIndicator />
                <DownloadList />
              </div>
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        {/* Premium Plans Page */}
        <Route path="/premium-plans" element={<PremiumPlans />} />
      </Routes>
    </Router>
  );
}

export default App;

