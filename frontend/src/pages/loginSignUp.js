import React, { useState } from "react";
import axios from "axios"; // Import Axios for API calls
import "./loginSignUp.css";

const LoginSignup = ({ setIsAuthenticated }) => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isSignUp) {
        // Sign-Up API Call
        const response = await axios.post("http://localhost:5000/signup", {
          email,
          password,
        });
        if (response.data.status === "success") {
          alert("Account created successfully!");
          setIsAuthenticated(true);
        } else {
          alert(response.data.message);
        }
      } else {
        // Log-In API Call
        const response = await axios.post("http://localhost:5000/login", {
          email,
          password,
        });
        if (response.data.status === "success") {
          alert("Logged in successfully!");
          setIsAuthenticated(true);
        } else {
          alert(response.data.message);
        }
      }
    } catch (error) {
      console.error("Error during authentication:", error);
      alert("Authentication failed. Please try again.");
    }
  };

  return (
    <div className="container">
      <h1 className="title">
        <span className="title-part first">ju</span>
        <span className="title-part middle">PDF</span>
        <span className="title-part last">ter</span>
      </h1>
      <div className="form-box">
        <h2 className="heading">{isSignUp ? "Sign Up" : "Log In"}</h2>
        <form className="form" onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            className="input email-input"
            value={email}
            onChange={(e) => setEmail(e.target.value)} // Capture email input
            required
          />
          <input
            type="password"
            placeholder="Password"
            className="input password-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)} // Capture password input
            required
          />
          <button type="submit" className="submit-button">
            {isSignUp ? "Sign Up" : "Log In"}
          </button>
        </form>
        <p
          className="toggle-form"
          onClick={() => setIsSignUp(!isSignUp)}
        >
          {isSignUp
            ? "Already have an account? Log in"
            : "Don't have an account? Sign up"}
        </p>
      </div>
    </div>
  );
};

export default LoginSignup;
