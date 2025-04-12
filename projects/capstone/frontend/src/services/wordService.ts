// src/services/wordService.ts
// Word-related API services

import { apiRequest } from './api';
import { Word } from '../types/word';

/**
 * Get words filtered by TOPIK level
 */
export async function getWordsByTopikLevel(level: number): Promise<Word[]> {
  return apiRequest<Word[]>(`words/topik/${level}`);
}

/**
 * Get most common words
 */
export async function getCommonWords(limit: number = 100): Promise<Word[]> {
  return apiRequest<Word[]>(`words/common?limit=${limit}`);
}

/**
 * Save a word to the user's collection
 */
export async function saveWord(word: Word): Promise<{ success: boolean }> {
  return apiRequest<{ success: boolean }>('words/save', {
    method: 'POST',
    body: { word },
  });
}

/**
 * Perform semantic search for related words
 */
export async function semanticSearch(query: string, limit: number = 5): Promise<Word[]> {
  return apiRequest<Word[]>('words/semantic-search', {
    method: 'POST',
    body: { query, limit },
  });
}