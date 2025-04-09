import React from 'react';
import './LoadingIndicator.css';

export default function LoadingIndicator() {
  return (
    <div className="loading-indicator">
      <div className="spinner"></div>
      <p>Loading...</p>
    </div>
  );
}