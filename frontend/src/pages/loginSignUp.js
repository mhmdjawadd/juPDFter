import React, { useState } from "react";
import "./loginSignUp.css";

const LoginSignup = ({ setIsAuthenticated }) => {
  const [isSignUp, setIsSignUp] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    // Simulate authentication and redirect
    setIsAuthenticated(true);
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
          />
          <input
            type="password"
            placeholder="Password"
            className="input password-input"
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
