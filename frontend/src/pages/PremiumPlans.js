import React from 'react';
import './PremiumPlans.css'; // Optional: Add styles for the page

const PremiumPlans = () => {
  return (
    <div className="premium-plans">
      <h1 className="premium-plans-title">Premium Plans</h1>
      <div className="plans">
        <div className="plan">
          <h3 className="mini-titles">Basic Plan</h3>
          <p className="free">Free</p>
          <p  className="limited-document-upload"> Limited document uploads </p>
          <p className="limited-document-processing"> Limited document processing </p>
          <button className="s1">Subscribe</button>
        </div>
        <div className="plan">
          <h3 className="mini-titles">Pro Plan</h3>
          <p className="pro">$10/month</p>
          <p className="unlimited-uploads">Unlimited uploads</p>
          <p className="advanced-ai">Advanced AI features</p>
          <p className="priority-support">Priority support</p>
          <button className="s2">Subscribe</button>
        </div>
        <div className="plan">
          <h3 className="mini-titles">Enterprise Plan</h3>
          <p className="custom">Custom</p>
          <button className="s3">Subscribe</button>
        </div>
      </div>
    </div>
  );
};

export default PremiumPlans;
