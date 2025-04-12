// src/store/theme.ts
// Theme state management

import { create } from 'zustand';

interface ThemeStore {
  theme: string;
  setTheme: (theme: string) => void;
}

export const useThemeStore = create<ThemeStore>((set) => ({
  theme: 'light',
  setTheme: (theme) => set({ theme }),
}));