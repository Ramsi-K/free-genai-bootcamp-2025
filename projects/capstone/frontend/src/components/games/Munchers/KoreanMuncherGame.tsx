import React, { useState, useEffect } from 'react';
import Sketch from 'react-p5';
import p5Types from 'p5';
import { api } from '../../lib/api';
import { Word, Group, Enemy, GameState } from './types';
import axios from 'axios';

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
  const GRID_SIZE = 4;
  const CANVAS_SIZE = Math.min(window.innerWidth * 0.7, 1000);
  const CELL_SIZE = CANVAS_SIZE / GRID_SIZE;

  const [words, setWords] = useState<string[][]>([]);
  const [themeWords, setThemeWords] = useState<Word[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [gameState, setGameState] = useState<GameState>('menu');
  const [currentState, setCurrentState] = useState<GameState>('menu');

  const [gameStats, setGameStats] = useState({
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

  const startGame = () => {
    setGameState('playing');
    setupLevel();
  };

  useEffect(() => {
    const loadThemeWords = async () => {
      setIsLoading(true);
      try {
        const groupWords = await api.getGroupWords(themeId);
        setThemeWords(groupWords);

        const grid = Array(GRID_SIZE).fill(null).map(() => 
          Array(GRID_SIZE).fill(null).map(() => {
            const randomIndex = Math.floor(Math.random() * groupWords.length);
            return groupWords[randomIndex].hangul;
          })
        );
        setWords(grid);
        startGame();
      } catch (error) {
        console.error('Failed to load theme words:', error);
      } finally {
        setIsLoading(false);
      }
    };

    if (themeId) {
      loadThemeWords();
    }
  }, [themeId]);

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
        // Random movement
        const directions = [[0, 1], [1, 0], [0, -1], [-1, 0]];
        const newDirection = Math.floor(Math.random() * directions.length);
        const [dx, dy] = directions[newDirection];
        const newX = enemy.x + dx;
        const newY = enemy.y + dy;
        
        if (newX >= 0 && newX < GRID_SIZE && newY >= 0 && newY < GRID_SIZE) {
          enemy.x = newX;
          enemy.y = newY;
          enemy.direction = newDirection;
        }
      }
      return enemy;
    }));
  };

  const checkCollisions = () => {
    enemies.forEach(enemy => {
      if (enemy.x === player.x && enemy.y === player.y && !gameStats.isGameOver) {
        setGameStats(prev => {
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
    if (gameStats.isGameOver) return;
    
    let selectedWord = words[player.y][player.x];
    if (themeWords.some(word => word.hangul === selectedWord)) {
      setGameStats(prev => {
        const newMunchMeter = prev.munchMeter + 1;
        const newScore = prev.score + (100 * prev.level);
        
        if (newMunchMeter >= 5) {
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
        newWords[player.y][player.x] = '';
        return newWords;
      });
    } else {
      setGameStats(prev => {
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
    if (gameStats.isGameOver) return;
    
    if (p5.keyCode === p5.LEFT_ARROW) player.move(-1, 0);
    if (p5.keyCode === p5.RIGHT_ARROW) player.move(1, 0);
    if (p5.keyCode === p5.UP_ARROW) player.move(0, -1);
    if (p5.keyCode === p5.DOWN_ARROW) player.move(0, 1);
    if (p5.keyCode === p5.ENTER || p5.keyCode === 32) handleWordMunch();
  };

  const setup = (p5: p5Types, canvasParentRef: Element) => {
    p5.createCanvas(CANVAS_SIZE, CANVAS_SIZE).parent(canvasParentRef);
  };

  const drawGrid = (p5: p5Types) => {
    const xOffset = (p5.width - GRID_SIZE * CELL_SIZE) / 2;
    const yOffset = 80;
    p5.stroke(74, 144, 226);
    p5.strokeWeight(2);
    for (let i = 0; i < GRID_SIZE; i++) {
      for (let j = 0; j < GRID_SIZE; j++) {
        p5.fill(10, 10, 40, 200);
        p5.rect(i * CELL_SIZE + xOffset, j * CELL_SIZE + yOffset, CELL_SIZE, CELL_SIZE);
      }
    }
  };

  const drawWords = (p5: p5Types) => {
    const xOffset = (p5.width - GRID_SIZE * CELL_SIZE) / 2;
    const yOffset = 80;
    p5.textAlign(p5.CENTER, p5.CENTER);
    p5.textSize(CELL_SIZE * 0.4);
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
    p5.fill(74, 144, 226);
    p5.noStroke();
    p5.circle(
      player.x * CELL_SIZE + CELL_SIZE / 2 + xOffset,
      player.y * CELL_SIZE + CELL_SIZE / 2 + yOffset,
      CELL_SIZE * 0.7
    );
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
      p5.fill(255, 50, 50);
      p5.noStroke();
      p5.circle(
        enemy.x * CELL_SIZE + CELL_SIZE / 2 + xOffset,
        enemy.y * CELL_SIZE + CELL_SIZE / 2 + yOffset,
        CELL_SIZE * 0.6
      );
    });
  };

  const draw = (p5: p5Types) => {
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
    if (!gameStats.isGameOver) {
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
    p5.text(`Level ${gameStats.level}  Score: ${gameStats.score}  Lives: ${gameStats.lives}`, CANVAS_SIZE/2, 50);
    p5.fill(50, 200, 50);
    p5.rect(100, CANVAS_SIZE - 30, gameStats.munchMeter * 40, 10);
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
            <span>Score: {gameStats.score}</span>
            <span>Lives: {gameStats.lives}</span>
            <span>Level: {gameStats.level}</span>
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