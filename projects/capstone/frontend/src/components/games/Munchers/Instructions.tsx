import React from 'react';

interface InstructionsProps {
  onStart: () => void;
  onBack: () => void;
  difficulty: string;
  themeName: string;
}

const Instructions: React.FC<InstructionsProps> = ({ 
  onStart, 
  onBack,
  difficulty,
  themeName 
}) => {
  return (
    <div className="glassmorphism p-8 max-w-2xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold neon-text mb-4">Get Ready!</h2>
      <div className="mb-6">
        <p className="text-xl">Level: <span className="neon-text">{difficulty}</span></p>
        <p className="text-xl">Theme: <span className="neon-text">{themeName}</span></p>
      </div>
      <ul className="space-y-4 text-lg">
        <li>🎮 Use arrow keys to move your character</li>
        <li>🎯 Move to a Korean word that matches the current theme</li>
        <li>⌨️ Press ENTER/SPACE to munch the word</li>
        <li>❤️ You have 3 lives - don't munch wrong words!</li>
        <li>👻 Avoid the red ghosts</li>
        <li>⭐ Level up after 5 correct munches</li>
      </ul>
      <div className="flex gap-4 mt-8">
        <button 
          onClick={onBack}
          className="btn-futuristic w-1/3"
        >
          Back
        </button>
        <button 
          onClick={onStart}
          className="btn-futuristic neon-glow w-2/3"
        >
          Start Game
        </button>
      </div>
    </div>
  );
};

export default Instructions;
