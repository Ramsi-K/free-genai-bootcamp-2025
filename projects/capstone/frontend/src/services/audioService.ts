// src/services/audioService.ts
// Audio and TTS-related services

import { apiRequest } from './api';

/**
 * Get pronunciation audio for a word
 */
export async function getPronunciation(text: string, language: string = 'ko'): Promise<Blob> {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/tts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text,
      language,
    }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to get pronunciation');
  }
  
  return await response.blob();
}

/**
 * Play audio from a blob
 */
export function playAudio(audioBlob: Blob): Promise<void> {
  return new Promise((resolve, reject) => {
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    
    audio.onended = () => {
      URL.revokeObjectURL(audioUrl);
      resolve();
    };
    
    audio.onerror = (error) => {
      URL.revokeObjectURL(audioUrl);
      reject(error);
    };
    
    audio.play().catch(reject);
  });
}