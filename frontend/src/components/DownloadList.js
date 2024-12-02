// src/components/DownloadList.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import "./DownloadList.css"; // Import the CSS file for styling

const DownloadList = () => {
  const [notebooks, setNotebooks] = useState([]); // State to hold the list of notebooks

  useEffect(() => {
    // Fetch the list of downloadable notebooks from the backend
    const fetchNotebooks = async () => {
      try {
        const response = await axios.get("http://localhost:5000/download/list");
        setNotebooks(response.data);
      } catch (error) {
        console.error("Error fetching notebooks:", error);
      }
    };

    fetchNotebooks();
  }, []);

  return (
    <div className="download-list-container">
      <h3 className="download-list-heading">Download Generated Notebooks</h3>
      {notebooks.length > 0 ? (
        <ul className="notebook-list">
          {notebooks.map((notebook, index) => (
            <li key={index} className="notebook-item">
              <a
                href={`http://localhost:5000${notebook.path}`}
                className="download-link"
                download
              >
                {notebook.name}
              </a>
            </li>
          ))}
        </ul>
      ) : (
        <p className="no-notebooks">No notebooks available for download 😞 </p>
      )}
    </div>
  );
};

export default DownloadList;
