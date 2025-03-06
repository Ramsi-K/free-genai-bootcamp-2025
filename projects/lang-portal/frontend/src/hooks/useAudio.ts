// src/hooks/useAudio.ts
// Custom hook for audio functionality

import { useState, useCallback, useEffect } from 'react';
import { getPronunciation, playAudio } from '../services/audioService';

export function useAudio() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [audioCache, setAudioCache] = useState<Record<string, Blob>>({});

  // Clean up audio cache when component unmounts
  useEffect(() => {
    return () => {
      // Revoke any object URLs that might be in memory
      Object.values(audioCache).forEach(() => {
        // In a real implementation, we would revoke URLs here
      });
    };
  }, [audioCache]);

  const pronunciationWithCache = useCallback(
    async (text: string, language: string = 'ko'): Promise<void> => {
      if (isPlaying) return;

      try {
        setIsPlaying(true);
        setError(null);

        let audioBlob: Blob;
        const cacheKey = `${language}:${text}`;

        // Check if we have this audio in cache
        if (audioCache[cacheKey]) {
          audioBlob = audioCache[cacheKey];
        } else {
          // If not in cache, fetch it and store
          audioBlob = await getPronunciation(text, language);
          setAudioCache((prev) => ({
            ...prev,
            [cacheKey]: audioBlob,
          }));
        }

        await playAudio(audioBlob);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to play audio');
        console.error('Audio playback error:', err);
      } finally {
        setIsPlaying(false);
      }
    },
    [isPlaying, audioCache]
  );

  return {
    pronunciationWithCache,
    isPlaying,
    error,
  };
}
