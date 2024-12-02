import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import FileUpload from './components/FileUpload';
import ProgressIndicator from './components/ProgressIndicator';
import DownloadList from './components/DownloadList';
import LoginSignup from './pages/loginSignUp';
import axios from 'axios'; // Import Axios for API calls

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false); // Track login status

  // Logout function
  const handleLogout = async () => {
    try {
      const response = await axios.post('http://localhost:5000/logout', {}, { withCredentials: true });
      if (response.data.status === 'success') {
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
              <Navigate to="/dashboard" replace />
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
                </button> {/* Add Logout Button */}
                <FileUpload />
                <ProgressIndicator />
                <DownloadList />
              </div>
            ) : (
              <Navigate to="/" replace />
            )
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
