// ProgressIndicator.js
import React, { useState, useEffect } from "react";
import axios from "axios";
import "./ProgressIndicator.css"; // Import CSS for styling

const ProgressIndicator = () => {
  const [status, setStatus] = useState("Waiting"); // Initial status
  const [progress, setProgress] = useState(0); // Initial progress (0%)

  // Polling backend for status updates
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        // const response = await axios.get("http://localhost:5000/process"); // Fetch status from backend
        // setStatus(response.data.status);
        // setProgress(response.data.progress); // Backend should send progress percentage
      } catch (error) {
        console.error("Error fetching progress:", error);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(interval); // Cleanup on component unmount
  }, []);

  return (
    <div className="progress-indicator-container">
      <div className="status-message">Document Processing Status: {status}</div>
      <div className="progress-bar-container">
        <div className="progress-bar" style={{ width: `${progress}%` }}>
          {progress}%
        </div>
      </div>
    </div>
  );
};

export default ProgressIndicator;
