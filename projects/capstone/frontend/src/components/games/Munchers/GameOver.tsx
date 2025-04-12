import React from 'react';

interface GameOverProps {
  score: number;
  onRestart: () => void;
}

const GameOver: React.FC<GameOverProps> = ({ score, onRestart }) => {
  return (
    <div className="glassmorphism p-8 text-center space-y-6">
      <h2 className="text-3xl font-bold neon-text">Game Over!</h2>
      <p className="text-2xl">Final Score: {score}</p>
      <button 
        onClick={onRestart}
        className="btn-futuristic neon-glow"
      >
        Play Again
      </button>
    </div>
  );
};

export default GameOver;
