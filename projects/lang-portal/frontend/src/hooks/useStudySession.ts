// src/hooks/useStudySession.ts
// Custom hook for tracking study sessions

import { useState, useEffect, useCallback } from 'react';
import { useLocalStorage } from './useLocalStorage';
import { StudyRecord } from '../types/study';
import { Word } from '../types/word';

export function useStudySession(sessionType: 'word' | 'listening' | 'sentence' | 'grammar') {
  const [sessionStartTime] = useState<Date>(new Date());
  const [elapsedTime, setElapsedTime] = useState(0);
  const [correctCount, setCorrectCount] = useState(0);
  const [incorrectCount, setIncorrectCount] = useState(0);
  const [streak, setStreak] = useState(0);
  const [lastStudyDate, setLastStudyDate] = useLocalStorage<string>('last-study-date', '');
  
  // Store study records in local storage
  const [studyHistory, setStudyHistory] = useLocalStorage<StudyRecord[]>('study-history', []);
  
  // Update elapsed time every second
  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      const elapsed = Math.floor((now.getTime() - sessionStartTime.getTime()) / 1000);
      setElapsedTime(elapsed);
    }, 1000);
    
    return () => clearInterval(timer);
  }, [sessionStartTime]);
  
  // Check and update streak
  useEffect(() => {
    const today = new Date().toISOString().split('T')[0];
    if (lastStudyDate) {
      const lastDate = new Date(lastStudyDate);
      const diff = Math.floor((Date.now() - lastDate.getTime()) / (1000 * 60 * 60 * 24));
      
      if (diff === 1) {
        setStreak(prev => prev + 1);
      } else if (diff > 1) {
        setStreak(0);
      }
    }
    setLastStudyDate(today);
  }, [lastStudyDate]);
  
  // Record study attempt
  const recordAttempt = useCallback(
    (word: Word, isCorrect: boolean) => {
      // Update counters
      if (isCorrect) {
        setCorrectCount((prev) => prev + 1);
      } else {
        setIncorrectCount((prev) => prev + 1);
      }
      
      // Create record
      const newRecord: StudyRecord = {
        id: Date.now(),
        wordId: word.id,
        timestamp: new Date().toISOString(),
        isCorrect,
        timeSpent: 0, // We could calculate this more precisely in a real app
      };
      
      // Add to history
      setStudyHistory((prev) => [...prev, newRecord]);
      
      return newRecord;
    },
    [setStudyHistory]
  );
  
  // Format time display (MM:SS)
  const formatTime = useCallback((seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
  }, []);
  
  // End session and get summary
  const endSession = useCallback(() => {
    const endTime = new Date();
    const totalTimeSpent = Math.floor((endTime.getTime() - sessionStartTime.getTime()) / 1000);
    
    return {
      sessionType,
      startTime: sessionStartTime.toISOString(),
      endTime: endTime.toISOString(),
      totalTimeSpent,
      correctCount,
      incorrectCount,
      totalAttempts: correctCount + incorrectCount,
      accuracy: correctCount / (correctCount + incorrectCount || 1) * 100,
    };
  }, [sessionType, sessionStartTime, correctCount, incorrectCount]);
  
  return {
    elapsedTime,
    formattedTime: formatTime(elapsedTime),
    correctCount,
    incorrectCount,
    recordAttempt,
    endSession,
    streak,
    sessionProgress: (correctCount / (correctCount + incorrectCount || 1)) * 100,
  };
}
