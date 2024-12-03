import React, { useState } from "react";
import "./loginSignUp.css";

const LoginSignup = ({ setIsAuthenticated }) => {
  const [isSignUp, setIsSignUp] = useState(false);
  const handleSubmit = (e) => {
    e.preventDefault();

    // Extract form values
    const username = e.target[0].value;
    const password = isSignUp ? e.target[1].value : null; // Email is required only for signup
    const email = isSignUp ? e.target[2].value : e.target[1].value;
    // Set the URL based on the operation (signup or login)
    const url = isSignUp ? "/signup" : "/login";

    // Construct the request body
    const body = isSignUp
      ? { username, email, password }
      : { username, password };

    // Call the backend API
    fetch(`http://localhost:5000${url}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "success") {
          setIsAuthenticated(true);
          // Mark the user as authenticated
          console.log(data.message); // Show a success message from the backend
        } else {
          alert(data.message); // Show an error message from the backend
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
      });
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
            type="text"
            placeholder="Username"
            className="input username-input"
          />
          <input
            type="password"
            placeholder="Password"
            className="input password-input"
          />
          {isSignUp && (
            <input
              type="email"
              placeholder="Email"
              className="input email-input"
            />
          )}
          <button type="submit" className="submit-button">
            {isSignUp ? "Sign Up" : "Log In"}
          </button>
        </form>
        <p className="toggle-form" onClick={() => setIsSignUp(!isSignUp)}>
          {isSignUp
            ? "Already have an account? Log in"
            : "Don't have an account? Sign up"}
        </p>
      </div>
    </div>
  );
};

export default LoginSignup;
