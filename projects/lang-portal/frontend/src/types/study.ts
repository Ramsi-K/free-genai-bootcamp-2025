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