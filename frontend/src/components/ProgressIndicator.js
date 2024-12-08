// ProgressIndicator.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ProgressIndicator.css'; // Import CSS for styling

const ProgressIndicator = () => {
  const [status, setStatus] = useState('Waiting'); // Initial status

  // Polling backend for status updates
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get("http://localhost:5000/process",{
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }); // Fetch status from backend
        setStatus(response.data.status);
      } catch (error) {
        console.error("Error fetching progress:", error);
      }
    }, 20000); // Poll every 20 seconds

    return () => clearInterval(interval); // Cleanup on component unmount
  }, []);

  return (
    <div className="progress-indicator-container">
      <div className="status-message">Document Processing Status: {status}</div>
    </div>
  );
};

export default ProgressIndicator;
