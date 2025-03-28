import p5Types from 'p5';

export interface Player {
  x: number;
  y: number;
  move: (dx: number, dy: number) => void;
  show: (p5: p5Types, cellSize: number, xOffset: number, yOffset: number) => void;
}

export interface Enemy {
  x: number;
  y: number;
  direction: number;
  moveTimer: number;
}

export type GameState = 'menu' | 'theme-select' | 'instructions' | 'playing' | 'paused' | 'game-over';
