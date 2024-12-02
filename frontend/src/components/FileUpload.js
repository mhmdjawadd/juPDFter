// FileUpload.js
import React, { useState } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css'; // Bootstrap for basic styling
import './FileUpload.css'; // Custom CSS file for component-specific styles

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async (event) => {
    event.preventDefault();
    if (!file) {
      setMessage("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://localhost:5000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setMessage("File uploaded successfully!");
    } catch (error) {
      console.error("Error uploading file:", error);
      setMessage("File upload failed.");
    }
  };

  return (
    <div className="file-upload-container">
      <h3 className="file-upload-heading">Hi there! Upload your document below.</h3>
      <form onSubmit={handleUpload}>
        <div className="file-input">
          <input
            type="file"
            className="form-control"
            onChange={handleFileChange}
          />
        </div>
        <button type="submit" className="btn upload-button">Upload</button>
      </form>
      {message && <div className="upload-message alert alert-info">{message}</div>}
    </div>
  );
};

export default FileUpload;
