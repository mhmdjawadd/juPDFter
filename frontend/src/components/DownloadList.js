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
        const response = await axios.get("http://localhost:5000/download/status");
        if (response.data.status === "fetched") {
          setNotebooksFetched(true);
          setMessage("Notebooks Generated! Please check your local downloads folder.");
        }
      } catch (error) {
        console.error("Error checking notebook status:", error);
      }
    };

    checkNotebooksStatus();
  }, []);

  return (
    <div className="download-list-container">
      <p className="notebook-message">{message}</p>
    </div>
  );
};

export default DownloadList;
