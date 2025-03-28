// src/types/word.ts
// Type definitions for words

export interface Word {
    id: number;
    korean: string;
    romanization: string;
    english: string;
    example: string;
    topikLevel?: number;
    frequency?: number;
    saved?: boolean;
  }
  
  export interface WordSearchResult {
    word: Word;
    similarity: number;
  }
  
  export type PracticeMode = 'topik' | 'common' | null;
  export type TopikLevel = 1 | 2 | 3 | 4 | 5 | 6 | null;
  
 