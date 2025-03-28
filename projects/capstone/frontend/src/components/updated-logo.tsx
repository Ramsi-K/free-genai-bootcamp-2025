import React from 'react';

const HagXwonLogo = ({ size = 'md', variant = 'blue-purple' }) => {
  // Size variants
  const sizes = {
    sm: 'w-6 h-6',
    md: 'w-10 h-10',
    lg: 'w-16 h-16',
    xl: 'w-24 h-24'
  };
  
  // Color variants based on the branding guide
  const colors = {
    'blue-purple': {
      left: '#4A90E2',
      right: '#6B2FB3',
      x: '#2D3748'
    },
    'purple': {
      left: '#6B2FB3',
      right: '#6B2FB3',
      x: '#2D3748'
    },
    'blue': {
      left: '#4A90E2',
      right: '#4A90E2',
      x: '#2D3748'
    },
    'gradient': {
      left: '#4A90E2',
      right: '#6B2FB3',
      x: '#2D3748',
      isGradient: true
    }
  };
  
  const currentColor = colors[variant] || colors['blue-purple'];
  const sizeClass = sizes[size] || sizes.md;

  return (
    <div className={`relative ${sizeClass}`}>
      <svg viewBox="0 0 300 150" xmlns="http://www.w3.org/2000/svg">
        {/* Define gradient if needed */}
        {currentColor.isGradient && (
          <defs>
            <linearGradient id="brandGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#4A90E2" />
              <stop offset="100%" stopColor="#6B2FB3" />
            </linearGradient>
          </defs>
        )}
        
        {/* The 'E' part */}
        <path 
          d="M30,60 H100 M30,75 H80 M30,90 H100" 
          stroke={currentColor.isGradient ? "url(#brandGradient)" : currentColor.left} 
          strokeWidth="20" 
          strokeLinecap="round" 
        />
        
        {/* The 'X' part */}
        <path 
          d="M130,40 L210,110 M210,40 L130,110" 
          stroke={currentColor.x} 
          strokeWidth="25" 
          strokeLinecap="round" 
        />
        
        {/* The 'O' part */}
        <circle 
          cx="250" 
          cy="75" 
          r="35" 
          stroke={currentColor.isGradient ? "url(#brandGradient)" : currentColor.right} 
          strokeWidth="20" 
          fill="none" 
        />
        <circle 
          cx="250" 
          cy="75" 
          r="15" 
          fill={currentColor.isGradient ? "url(#brandGradient)" : currentColor.right} 
        />
      </svg>
    </div>
  );
};

export default HagXwonLogo;
