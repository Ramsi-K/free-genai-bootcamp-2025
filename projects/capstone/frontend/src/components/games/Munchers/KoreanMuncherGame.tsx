import React, { useState, useEffect } from 'react';
import Sketch from 'react-p5';
import p5Types from 'p5';
import { api } from '../../lib/api';
import { Word } from '../../types/api';

interface KoreanMuncherGameProps {
  difficulty: string;
  themeId: number;
  onGameOver: (score: number) => void;
  onPause: () => void;
}

interface DifficultySettings {
  enemySpeed: number;
  enemyCount: number;
  lives: number;
}

const DIFFICULTY_SETTINGS: Record<string, DifficultySettings> = {
  beginner: {
    enemySpeed: 60,  // Slower enemies
    enemyCount: 2,   // Fewer enemies
    lives: 5         // More lives
  },
  intermediate: {
    enemySpeed: 45,
    enemyCount: 3,
    lives: 3
  },
  advanced: {
    enemySpeed: 30,  // Faster enemies
    enemyCount: 4,   // More enemies
    lives: 2         // Fewer lives
  }
};

const KoreanMuncherGame: React.FC<KoreanMuncherGameProps> = ({
  difficulty,
  themeId,
  onGameOver,
  onPause
}) => {
  const GRID_SIZE = 4; // Changed from 5 to 4 rows
  const CANVAS_SIZE = Math.min(window.innerWidth * 0.7, 1000); // Increased max width
  const CELL_SIZE = CANVAS_SIZE / GRID_SIZE;

  const [words, setWords] = useState<string[][]>([]);
  const [themeWords, setThemeWords] = useState<Word[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const [gameState, setGameState] = useState({
    score: 0,
    lives: DIFFICULTY_SETTINGS[difficulty].lives,
    munchMeter: 0,
    level: 1,
    isGameOver: false
  });

  const initializePlayer = () => ({
    x: Math.floor(GRID_SIZE / 2),
    y: Math.floor(GRID_SIZE / 2),
    move: function(dx: number, dy: number) {
      const newX = this.x + dx;
      const newY = this.y + dy;
      if (newX >= 0 && newX < GRID_SIZE && newY >= 0 && newY < GRID_SIZE) {
        this.x = newX;
        this.y = newY;
      }
    }
  });

  const [player, setPlayer] = useState(initializePlayer());
  const [enemies, setEnemies] = useState<Enemy[]>([]);

  const resetPlayerPosition = () => {
    setPlayer(initializePlayer());
  };

  const difficultySettings = DIFFICULTY_SETTINGS[difficulty];

  useEffect(() => {
    const loadThemeWords = async () => {
      setIsLoading(true);
      try {
        // Get all words for this theme
        const groupWords = await api.getGroupWords(themeId);
        setThemeWords(groupWords);

        // Create grid with random selection of words
        const grid = Array(GRID_SIZE).fill(null).map(() => 
          Array(GRID_SIZE).fill(null).map(() => {
            const randomIndex = Math.floor(Math.random() * groupWords.length);
            return groupWords[randomIndex].hangul;
          })
        );
        setWords(grid);
      } catch (error) {
        console.error('Failed to load theme words:', error);
      }
      setIsLoading(false);
    };
    loadThemeWords();
  }, [themeId]);

  const setup = (p5: p5Types, canvasParentRef: Element) => {
    p5.createCanvas(CANVAS_SIZE, CANVAS_SIZE).parent(canvasParentRef);
    setupLevel();
    // ...rest of setup
  };

  const setupLevel = () => {
    const newEnemies: Enemy[] = [];
    for (let i = 0; i < difficultySettings.enemyCount; i++) {
      newEnemies.push({
        x: Math.floor(Math.random() * GRID_SIZE),
        y: Math.floor(Math.random() * GRID_SIZE),
        direction: Math.floor(Math.random() * 4),
        moveTimer: 0
      });
    }
    setEnemies(newEnemies);
  };

  const updateEnemies = (p5: p5Types) => {
    setEnemies(prevEnemies => prevEnemies.map(enemy => {
      enemy.moveTimer++;
      if (enemy.moveTimer > difficultySettings.enemySpeed) {
        enemy.moveTimer = 0;
        // ...rest of enemy movement code...
      }
      return enemy;
    }));
  };

  const checkCollisions = () => {
    enemies.forEach(enemy => {
      if (enemy.x === player.x && enemy.y === player.y && !gameState.isGameOver) {
        setGameState(prev => {
          const newLives = prev.lives - 1;
          if (newLives <= 0) {
            onGameOver(prev.score);
            return { ...prev, lives: 0, isGameOver: true };
          }
          return { ...prev, lives: newLives };
        });
        resetPlayerPosition();
      }
    });
  };

  const handleWordMunch = () => {
    if (gameState.isGameOver) return;
    
    let selectedWord = words[player.y][player.x];
    if (themeWords.some(word => word.hangul === selectedWord)) {
      setGameState(prev => {
        const newMunchMeter = prev.munchMeter + 1;
        const newScore = prev.score + (100 * prev.level);
        
        if (newMunchMeter >= 5) {
          // Level up after 5 correct munches
          return {
            ...prev,
            score: newScore,
            munchMeter: 0,
            level: prev.level + 1
          };
        }
        
        return {
          ...prev,
          score: newScore,
          munchMeter: newMunchMeter
        };
      });
      setWords(prevWords => {
        const newWords = [...prevWords];
        newWords[player.y][player.x] = ''; // Remove munched word
        return newWords;
      });
    } else {
      setGameState(prev => {
        const newLives = prev.lives - 1;
        if (newLives <= 0) {
          onGameOver(prev.score);
          return { ...prev, lives: 0, isGameOver: true };
        }
        return { ...prev, lives: newLives };
      });
      resetPlayerPosition();
    }
  };

  const keyPressed = (p5: p5Types) => {
    if (gameState.isGameOver) return;
    
    if (p5.keyCode === p5.LEFT_ARROW) player.move(-1, 0);
    if (p5.keyCode === p5.RIGHT_ARROW) player.move(1, 0);
    if (p5.keyCode === p5.UP_ARROW) player.move(0, -1);
    if (p5.keyCode === p5.DOWN_ARROW) player.move(0, 1);
    if (p5.keyCode === p5.ENTER || p5.keyCode === 32) handleWordMunch();
  };

  const drawGrid = (p5: p5Types) => {
    const xOffset = (p5.width - GRID_SIZE * CELL_SIZE) / 2;
    const yOffset = 80; // Reduced from 100 to 80 to fit better
    p5.stroke(74, 144, 226); // Restored original blue color
    p5.strokeWeight(2);
    for (let i = 0; i < GRID_SIZE; i++) {
      for (let j = 0; j < GRID_SIZE; j++) {
        p5.fill(10, 10, 40, 200); // Semi-transparent dark blue
        p5.rect(i * CELL_SIZE + xOffset, j * CELL_SIZE + yOffset, CELL_SIZE, CELL_SIZE);
      }
    }
  };

  const drawWords = (p5: p5Types) => {
    const xOffset = (p5.width - GRID_SIZE * CELL_SIZE) / 2;
    const yOffset = 80;
    p5.textAlign(p5.CENTER, p5.CENTER);
    p5.textSize(CELL_SIZE * 0.4); // Increased text size
    p5.fill(255);
    words.forEach((row, i) => {
      row.forEach((word, j) => {
        if (word) {
          p5.text(
            word,
            i * CELL_SIZE + CELL_SIZE / 2 + xOffset,
            j * CELL_SIZE + CELL_SIZE / 2 + yOffset
          );
        }
      });
    });
  };

  const drawPlayer = (p5: p5Types) => {
    const xOffset = (p5.width - GRID_SIZE * CELL_SIZE) / 2;
    const yOffset = 80;
    // Restore original player appearance
    p5.fill(74, 144, 226); // Primary blue
    p5.noStroke();
    p5.circle(
      player.x * CELL_SIZE + CELL_SIZE / 2 + xOffset,
      player.y * CELL_SIZE + CELL_SIZE / 2 + yOffset,
      CELL_SIZE * 0.7
    );
    // Add eyes
    p5.fill(255);
    p5.circle(
      player.x * CELL_SIZE + CELL_SIZE * 0.4 + xOffset,
      player.y * CELL_SIZE + CELL_SIZE * 0.4 + yOffset,
      CELL_SIZE * 0.15
    );
    p5.circle(
      player.x * CELL_SIZE + CELL_SIZE * 0.6 + xOffset,
      player.y * CELL_SIZE + CELL_SIZE * 0.4 + yOffset,
      CELL_SIZE * 0.15
    );
  };

  const drawEnemies = (p5: p5Types) => {
    const xOffset = (p5.width - GRID_SIZE * CELL_SIZE) / 2;
    const yOffset = 80;
    enemies.forEach(enemy => {
      p5.fill(255, 50, 50); // Bright red
      p5.noStroke();
      p5.circle(
        enemy.x * CELL_SIZE + CELL_SIZE / 2 + xOffset,
        enemy.y * CELL_SIZE + CELL_SIZE / 2 + yOffset,
        CELL_SIZE * 0.6
      );
    });
  };

  const draw = (p5: p5Types) => {
    // Background gradient
    const c1 = p5.color(10, 10, 40);
    const c2 = p5.color(20, 20, 80);
    for(let y = 0; y < p5.height; y++){
      const inter = y / p5.height;
      const c = p5.lerpColor(c1, c2, inter);
      p5.stroke(c);
      p5.line(0, y, p5.width, y);
    }
    
    drawGrid(p5);
    drawWords(p5);
    drawPlayer(p5);
    if (!gameState.isGameOver) {
      drawEnemies(p5);
      updateEnemies(p5);
      checkCollisions();
    }
    showHUD(p5);
  };

  const showHUD = (p5: p5Types) => {
    p5.fill(255);
    p5.textSize(24);
    p5.textAlign(p5.CENTER, p5.CENTER);
    p5.text(`Level ${gameState.level}  Score: ${gameState.score}  Lives: ${gameState.lives}`, CANVAS_SIZE/2, 50);
    // Draw munch meter
    p5.fill(50, 200, 50);
    p5.rect(100, CANVAS_SIZE - 30, gameState.munchMeter * 40, 10);
  };

  if (isLoading) {
    return <div className="text-center">Loading words...</div>;
  }

  return (
    <div className="game-container relative w-full max-w-5xl mx-auto">
      <div className="glassmorphism p-6 rounded-lg">
        <div className="flex justify-between items-center mb-4">
          <button 
            className="btn-futuristic"
            onClick={onPause}
          >
            Pause
          </button>
          <div className="flex gap-8 text-xl">
            <span>Score: {gameState.score}</span>
            <span>Lives: {gameState.lives}</span>
            <span>Level: {gameState.level}</span>
          </div>
        </div>
        <Sketch 
          setup={setup}
          draw={draw}
          keyPressed={keyPressed}
        />
      </div>
    </div>
  );
};

export default KoreanMuncherGame;
