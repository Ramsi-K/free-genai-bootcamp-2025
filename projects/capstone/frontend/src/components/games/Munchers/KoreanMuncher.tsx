import React, { useState, useEffect } from 'react';
import { api } from '../../../lib/api';
import ThemeSelector from './ThemeSelector';
import Instructions from './Instructions';
import GameOver from './GameOver';
import { Group } from '../../../types/api';

type GameState = 'level-select' | 'theme-select' | 'instructions' | 'playing' | 'paused' | 'game-over';

const KoreanMuncher: React.FC = () => {
  const [gameState, setGameState] = useState<GameState>('level-select');
  const [difficulty, setDifficulty] = useState('beginner');
  const [selectedTheme, setSelectedTheme] = useState<number | null>(null);
  const [selectedThemeName, setSelectedThemeName] = useState<string>('');
  const [themeGroups, setThemeGroups] = useState<Group[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadThemes = async () => {
      setIsLoading(true);
      try {
        const themes = await api.getGroups('theme');
        console.log('Themes from API:', themes);
        setThemeGroups(themes); // Just use the themes directly
        setError(null);
      } catch (err) {
        console.error('Failed to load themes:', err);
        setError('Failed to load themes');
      } finally {
        setIsLoading(false);
      }
    };

    loadThemes();
  }, []);

  const handleDifficultySelect = (level: string) => {
    console.log('Selected difficulty:', level);
    setDifficulty(level);
    setGameState('theme-select');
  };

  const handleThemeSelect = async (themeId: number) => {
    console.log('Selected theme ID:', themeId);
    try {
      const selectedTheme = themeGroups.find(theme => theme.id === themeId);
      if (!selectedTheme) {
        throw new Error('Theme not found');
      }
      console.log('Found theme:', selectedTheme);

      const words = await api.getGroupWords(themeId);
      console.log('Theme words:', words);

      if (!words || words.length === 0) {
        throw new Error('No words found for theme');
      }

      setSelectedTheme(themeId);
      setSelectedThemeName(selectedTheme.name);
      setGameState('instructions');
    } catch (error) {
      console.error('Failed to select theme:', error);
      setError('Failed to load theme words');
    }
  };

  return (
    <div className="flex flex-col items-center max-w-4xl mx-auto">
      <h1 className="text-4xl mb-8 neon-text">Korean Word Muncher</h1>
      
      {isLoading ? (
        <div className="text-center p-8">
          <div className="animate-spin h-8 w-8 border-4 border-primary-blue rounded-full border-t-transparent mx-auto mb-4"></div>
          <p className="text-lg opacity-70">Loading game...</p>
        </div>
      ) : (
        <>
          {error && (
            <div className="bg-red-500/20 border border-red-500/50 p-4 mb-8 rounded-lg">
              {error}
            </div>
          )}

          {gameState === 'level-select' && (
            <div className="glassmorphism p-8 w-full max-w-md space-y-6">
              <h2 className="text-2xl font-bold text-center mb-6">Choose your Level</h2>
              <div className="flex flex-col space-y-4">
                {['beginner', 'intermediate', 'advanced'].map(level => (
                  <button
                    key={level}
                    className={`btn-futuristic text-lg py-4 ${difficulty === level ? 'neon-glow' : ''}`}
                    onClick={() => handleDifficultySelect(level)}
                  >
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                    <span className="block text-sm opacity-70">
                      {level === 'beginner' ? 'Slower enemies, more lives' :
                       level === 'intermediate' ? 'Moderate speed, normal lives' :
                       'Fast enemies, fewer lives'}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {gameState === 'theme-select' && themeGroups && (
            <div className="glassmorphism p-8 w-full">
              <h2 className="text-2xl font-bold mb-6 text-center">Choose your Theme</h2>
              {themeGroups.length > 0 ? (
                <ThemeSelector 
                  themes={themeGroups} 
                  onSelect={handleThemeSelect}
                />
              ) : (
                <div className="text-center p-8">
                  <p className="text-lg opacity-70">No themes available</p>
                </div>
              )}
              <button 
                className="btn-futuristic mt-6 w-full"
                onClick={() => setGameState('level-select')}
              >
                Back to Level Select
              </button>
            </div>
          )}

          {gameState === 'instructions' && (
            <Instructions 
              onStart={() => setGameState('playing')}
              onBack={() => setGameState('theme-select')}
              difficulty={difficulty}
              themeName={selectedThemeName}
            />
          )}

          {gameState === 'playing' && selectedTheme && (
            <div className="game-container">
              <canvas></canvas>
            </div>
          )}

          {gameState === 'game-over' && (
            <GameOver
              score={0}
              onRestart={() => setGameState('level-select')}
            />
          )}
        </>
      )}
    </div>
  );
};

export default KoreanMuncher;
