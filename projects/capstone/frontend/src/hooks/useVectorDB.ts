// src/hooks/useVectorDB.ts
// Custom hook for vector DB operations

import { useState, useCallback } from 'react';
import { semanticVectorSearch, addToVectorDB } from '../services/vectorDBService';
import { Word } from '../types/word';

export function useVectorDB() {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<Word[]>([]);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (query: string, limit: number = 5) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const searchResults = await semanticVectorSearch(query, limit);
      setResults(searchResults);
      return searchResults;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error searching vector database';
      setError(errorMessage);
      console.error('Vector DB search error:', err);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addWord = useCallback(async (word: Word) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await addToVectorDB(word);
      return result.success;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error adding to vector database';
      setError(errorMessage);
      console.error('Vector DB add error:', err);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    search,
    addWord,
    results,
    isLoading,
    error,
  };
}
