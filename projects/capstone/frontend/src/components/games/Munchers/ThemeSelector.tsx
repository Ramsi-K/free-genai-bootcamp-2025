import React from 'react';
import { Group } from '../../../types/api';

interface ThemeSelectorProps {
  themes: Group[];
  onSelect: (themeId: number) => void;
}

const ThemeSelector: React.FC<ThemeSelectorProps> = ({ themes, onSelect }) => {
  console.log('Rendering themes:', themes); // Debug log

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {Array.isArray(themes) && themes.map((theme) => (
        <button
          key={theme.id}
          onClick={() => onSelect(theme.id)}
          className="p-4 glassmorphism hover:neon-glow transition-all duration-300 text-left"
        >
          <h3 className="text-xl font-bold mb-2">{theme.name}</h3>
          {theme.words_count > 0 && (
            <p className="text-sm opacity-70">{theme.words_count} word{theme.words_count !== 1 ? 's' : ''}</p>
          )}
        </button>
      ))}
    </div>
  );
};

export default ThemeSelector;
