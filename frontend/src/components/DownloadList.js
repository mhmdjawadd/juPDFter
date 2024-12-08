// src/components/DownloadList.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import "./DownloadList.css"; // Import the CSS file for styling

const DownloadList = () => {
  const [notebooksFetched, setNotebooksFetched] = useState(false); // State to track whether notebooks are fetched
  const [message, setMessage] = useState("Sorry, no notebooks to display."); // Initial message

  useEffect(() => {
    // Fetch the status of notebook generation from the backend
    const checkNotebooksStatus = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get("http://localhost:5000/download/status",
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
        
        if (response.data.status === "fetched") {
          setNotebooksFetched(true);
          setMessage("Notebooks Generated! Please check your local downloads folder.");
        }
      } catch (error) {
        console.error("Error checking notebook status:", error);
      }
    };

    // Initial check
    checkNotebooksStatus();

    // Set up polling interval - 20000ms = 20 seconds
    const interval = setInterval(checkNotebooksStatus, 20000);

    // Cleanup interval on component unmount
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="download-list-container">
      <p className="notebook-message">{message}</p>
    </div>
  );
};

export default DownloadList;
