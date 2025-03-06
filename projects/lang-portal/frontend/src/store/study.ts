// src/store/study.ts
// Study progress management

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { StudyRecord, StudySession, StudyStats } from '../types/study';
import { Word } from '../types/word';

interface StudyState {
  activeSession: StudySession | null;
  studyRecords: StudyRecord[];
  studySessions: StudySession[];
  
  // Actions
  startSession: (type: 'word' | 'listening' | 'sentence' | 'grammar') => void;
  endSession: (score?: number) => void;
  recordAttempt: (word: Word, isCorrect: boolean) => void;
  getStats: () => StudyStats;
  resetHistory: () => void;
}

export const useStudyStore = create<StudyState>()(
  persist(
    (set, get) => ({
      activeSession: null,
      studyRecords: [],
      studySessions: [],
      
      startSession: (type) => {
        // End any existing session first
        if (get().activeSession) {
          get().endSession();
        }
        
        const newSession: StudySession = {
          id: Date.now(),
          type,
          startTime: new Date().toISOString(),
          endTime: '',
          completed: false,
        };
        
        set({ activeSession: newSession });
      },
      
      endSession: (score) => {
        const { activeSession, studySessions } = get();
        
        if (!activeSession) return;
        
        const completedSession: StudySession = {
          ...activeSession,
          endTime: new Date().toISOString(),
          score,
          completed: true,
        };
        
        set({
          activeSession: null,
          studySessions: [...studySessions, completedSession],
        });
      },
      
      recordAttempt: (word, isCorrect) => {
        const { studyRecords, activeSession } = get();
        
        if (!activeSession) {
          // Auto-start a word session if none is active
          get().startSession('word');
        }
        
        const newRecord: StudyRecord = {
          id: Date.now(),
          wordId: word.id,
          timestamp: new Date().toISOString(),
          isCorrect,
        };
        
        set({ studyRecords: [...studyRecords, newRecord] });
      },
      
      getStats: () => {
        const { studyRecords, studySessions } = get();
        
        // Calculate total sessions by type
        const typeDistribution = {
          word: studySessions.filter(s => s.type === 'word').length,
          listening: studySessions.filter(s => s.type === 'listening').length,
          sentence: studySessions.filter(s => s.type === 'sentence').length,
          grammar: studySessions.filter(s => s.type === 'grammar').length,
        };
        
        // Calculate average score
        const sessionsWithScores = studySessions.filter(s => s.score !== undefined);
        const averageScore = sessionsWithScores.length 
          ? sessionsWithScores.reduce((sum, session) => sum + (session.score || 0), 0) / sessionsWithScores.length
          : 0;
        
        // Calculate success rate from study records
        const totalRecords = studyRecords.length;
        const correctRecords = studyRecords.filter(r => r.isCorrect).length;
        
        return {
          totalSessions: studySessions.length,
          averageScore,
          totalTimeSpent: 0, // This would require calculating time differences between start/end
          successRate: totalRecords ? (correctRecords / totalRecords) * 100 : 0,
          typeDistribution,
        };
      },
      
      resetHistory: () => {
        set({
          studyRecords: [],
          studySessions: [],
        });
      },
    }),
    {
      name: 'study-storage', // Name for the localStorage key
    }
  )
);