// src/store/words.ts
// Words data management

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Word } from '../types/word';

interface WordsState {
  words: Word[];
  savedWords: Word[];
  recentWords: Word[];
  isLoading: boolean;
  error: string | null;
  semanticSearchResults: Word[];
  semanticSearchLoading: boolean;
  
  // Actions
  fetchWordsByTopikLevel: (level: number) => Promise<void>;
  fetchCommonWords: (limit?: number) => Promise<void>;
  saveWord: (word: Word) => void;
  removeSavedWord: (wordId: number) => void;
  addToRecent: (word: Word) => void;
  clearRecentWords: () => void;
  semanticSearch: (query: string) => Promise<void>;
  clearSearchResults: () => void;
}

export const useWordsStore = create<WordsState>()(
  persist(
    (set, get) => ({
      words: [],
      savedWords: [],
      recentWords: [],
      isLoading: false,
      error: null,
      semanticSearchResults: [],
      semanticSearchLoading: false,
      
      fetchWordsByTopikLevel: async (level: number) => {
        set({ isLoading: true, error: null });
        try {
          // In a real implementation, this would be an API call
          // Placeholder implementation for now
          const mockWords: Word[] = Array(20).fill(null).map((_, i) => ({
            id: i + 1,
            korean: `한국어 단어 ${i + 1}`,
            romanization: `hangugeo daneo ${i + 1}`,
            english: `Korean word ${i + 1}`,
            example: `이것은 한국어 단어 ${i + 1}입니다.`,
            topikLevel: level,
            frequency: Math.floor(Math.random() * 100) + 1,
          }));
          
          setTimeout(() => {
            set({ words: mockWords, isLoading: false });
          }, 500);
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch words',
            isLoading: false,
          });
        }
      },
      
      fetchCommonWords: async (limit = 100) => {
        set({ isLoading: true, error: null });
        try {
          // Placeholder implementation
          const mockWords: Word[] = Array(limit).fill(null).map((_, i) => ({
            id: i + 100, // Offset IDs to avoid conflicts with other mocked words
            korean: `자주 쓰는 단어 ${i + 1}`,
            romanization: `jaju seuneun daneo ${i + 1}`,
            english: `Common word ${i + 1}`,
            example: `이 단어는 자주 사용합니다.`,
            frequency: i + 1, // Lower number means more common
          }));
          
          setTimeout(() => {
            set({ words: mockWords, isLoading: false });
          }, 500);
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch common words',
            isLoading: false,
          });
        }
      },
      
      saveWord: (word: Word) => {
        const { savedWords } = get();
        // Check if word is already saved to avoid duplicates
        if (!savedWords.some(saved => saved.id === word.id)) {
          set({ savedWords: [...savedWords, { ...word, saved: true }] });
        }
      },
      
      removeSavedWord: (wordId: number) => {
        const { savedWords } = get();
        set({ 
          savedWords: savedWords.filter(word => word.id !== wordId) 
        });
      },
      
      addToRecent: (word: Word) => {
        const { recentWords } = get();
        // Remove word if it's already in recents (to move it to the top)
        const filteredRecents = recentWords.filter(w => w.id !== word.id);
        // Add to the beginning of the array and limit to 20 recent words
        set({ 
          recentWords: [word, ...filteredRecents].slice(0, 20) 
        });
      },
      
      clearRecentWords: () => {
        set({ recentWords: [] });
      },
      
      semanticSearch: async (query: string) => {
        set({ semanticSearchLoading: true });
        try {
          const results = await semanticSearch(query);
          set({ semanticSearchResults: results, semanticSearchLoading: false });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Semantic search failed',
            semanticSearchLoading: false 
          });
        }
      },
      
      clearSearchResults: () => set({ semanticSearchResults: [] }),
    }),
    {
      name: 'words-storage', // Name for the localStorage key
      partialize: (state) => ({ savedWords: state.savedWords, recentWords: state.recentWords }),
    }
  )
);