// src/store/user.ts
// User data management

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UserState {
  name: string;
  level: string;
  streak: number;
  points: number;
  progress: number;
  isAuthenticated: boolean;
  
  // Actions
  updateUser: (data: Partial<UserState>) => void;
  incrementStreak: () => void;
  incrementPoints: (amount: number) => void;
  setProgress: (progress: number) => void;
  resetProgress: () => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      name: 'Language Learner',
      level: 'Beginner',
      streak: 0,
      points: 0,
      progress: 0,
      isAuthenticated: false,
      
      updateUser: (data) => set((state) => ({ ...state, ...data })),
      
      incrementStreak: () => set((state) => ({ streak: state.streak + 1 })),
      
      incrementPoints: (amount) => set((state) => ({ points: state.points + amount })),
      
      setProgress: (progress) => set({ progress }),
      
      resetProgress: () => set({ progress: 0 }),
    }),
    {
      name: 'user-storage', // Name for the localStorage key
    }
  )
);
