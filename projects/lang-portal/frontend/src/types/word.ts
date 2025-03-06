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
  
  // src/types/study.ts
  // Type definitions for study progress
  
  export interface StudySession {
    id: number;
    type: 'word' | 'listening' | 'sentence' | 'grammar';
    startTime: string;
    endTime: string;
    score?: number;
    completed: boolean;
  }
  
  export interface StudyRecord {
    id: number;
    wordId: number;
    timestamp: string;
    isCorrect: boolean;
    timeSpent?: number;
  }
  
  export interface StudyStats {
    totalSessions: number;
    averageScore: number;
    totalTimeSpent: number;
    typeDistribution: {
      word: number;
      listening: number;
      sentence: number;
      grammar: number;
    };
  }