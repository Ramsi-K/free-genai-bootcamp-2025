// src/services/vectorDBService.ts
// Vector DB integration services

import { apiRequest } from './api';
import { Word } from '../types/word';

/**
 * Add a word to the vector database
 */
export async function addToVectorDB(word: Word): Promise<{ success: boolean }> {
  return apiRequest<{ success: boolean }>('vector/add', {
    method: 'POST',
    body: { word },
  });
}

/**
 * Search for semantically similar words
 */
export async function semanticVectorSearch(query: string, limit: number = 5): Promise<Word[]> {
  return apiRequest<Word[]>('vector/search', {
    method: 'POST',
    body: { query, limit },
  });
}