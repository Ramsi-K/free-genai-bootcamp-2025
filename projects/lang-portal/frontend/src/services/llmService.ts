// src/services/llmService.ts
// LLM API integration

import { apiRequest } from './api';
import { Word } from '../types/word';

/**
 * Get more related words using LLM
 */
export async function getLLMSuggestions(
  word: Word,
  count: number = 5
): Promise<Word[]> {
  return apiRequest<Word[]>('llm/suggestions', {
    method: 'POST',
    body: {
      word,
      count,
    },
  });
}

/**
 * Generate example sentences using LLM
 */
export async function generateExamples(
  word: string,
  language: string = 'ko',
  count: number = 3
): Promise<string[]> {
  return apiRequest<string[]>('llm/examples', {
    method: 'POST',
    body: {
      word,
      language,
      count,
    },
  });
}