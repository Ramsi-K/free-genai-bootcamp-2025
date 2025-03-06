import React from 'react';

const HagXwonLogo = () => {
  return (
    <div className="relative w-10 h-10 flex items-center justify-center">
      {/* Outer ring with glow effect */}
      <div className="absolute inset-0 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 animate-pulse-glow"></div>
      
      {/* Inner container */}
      <div className="absolute inset-1 rounded-full bg-black/70 backdrop-blur-sm flex items-center justify-center">
        {/* Korean character "학" (hag) stylized */}
        <div className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 font-bold text-xl">
          학
        </div>
      </div>
      
      {/* Orbiting particle */}
      <div className="absolute w-2 h-2 rounded-full bg-blue-400 animate-float" 
           style={{
             top: '0px',
             left: '50%',
             transform: 'translateX(-50%)',
             boxShadow: '0 0 8px rgba(74, 144, 226, 0.8)'
           }}></div>
    </div>
  );
};

export default HagXwonLogo;
