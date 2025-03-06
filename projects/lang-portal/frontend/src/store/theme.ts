// src/store/theme.ts
// Theme state management

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type Theme = 'light' | 'dark';

interface ThemeState {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
  systemTheme: Theme | null;
  useSystemTheme: boolean;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: 'dark', // Default theme
      toggleTheme: () => set((state) => ({ theme: state.theme === 'dark' ? 'light' : 'dark' })),
      setTheme: (theme: Theme) => {
        set({ theme, useSystemTheme: false });
        document.documentElement.setAttribute('data-theme', theme);
      },
      systemTheme: null,
      useSystemTheme: true,
      initializeTheme: () => {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        const systemTheme = mediaQuery.matches ? 'dark' : 'light';
        set({ systemTheme });
        
        if (get().useSystemTheme) {
          document.documentElement.setAttribute('data-theme', systemTheme);
        }
        
        mediaQuery.addEventListener('change', (e) => {
          const newTheme = e.matches ? 'dark' : 'light';
          set({ systemTheme: newTheme });
          if (get().useSystemTheme) {
            document.documentElement.setAttribute('data-theme', newTheme);
          }
        });
      },
    }),
    {
      name: 'theme-storage', // Name for the localStorage key
    }
  )
);