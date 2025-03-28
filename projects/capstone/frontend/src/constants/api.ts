// src/constants/api.ts
// API constants

export const API_ENDPOINTS = {
    WORDS: {
      BY_TOPIK: (level: number) => `words/topik/${level}`,
      COMMON: 'words/common',
      SAVE: 'words/save',
      SEMANTIC_SEARCH: 'words/semantic-search',
    },
    AUDIO: {
      TTS: 'tts',
      PRONOUNCE: 'audio/pronounce',
    },
    VECTOR: {
      ADD: 'vector/add',
      SEARCH: 'vector/search',
    },
    LLM: {
      SUGGESTIONS: 'llm/suggestions',
      EXAMPLES: 'llm/examples',
    },
    USER: {
      PROFILE: 'user/profile',
      UPDATE: 'user/update',
    },
  };