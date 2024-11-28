import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import FileUpload from './components/FileUpload';
import ProgressIndicator from './components/ProgressIndicator';
import DownloadList from './components/DownloadList';
import LoginSignup from './pages/loginSignUp';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false); // Track login status

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
