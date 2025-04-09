import axios from 'axios';
import { cacheService } from './cacheService';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// API instance with default config and caching
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// API interceptors for caching
api.interceptors.request.use(async config => {
  if (config.method === 'get') {
    const cachedResponse = cacheService.get(config.url);
    if (cachedResponse) {
      return Promise.reject({
        response: { data: cachedResponse },
        cached: true
      });
    }
  }
  return config;
});

api.interceptors.response.use(
  response => {
    if (response.config.method === 'get') {
      cacheService.set(response.config.url, response.data);
    }
    return response;
  },
  error => {
    if (error.cached) {
      return Promise.resolve({ data: error.response.data });
    }
    const customError = {
      message: error.response?.data?.error || 'An unexpected error occurred',
      status: error.response?.status,
      details: error.response?.data?.details
    };
    return Promise.reject(customError);
  }
);

// Video related APIs
export const videoAPI = {
  getAll: () => api.get('/api/videos'),
  getById: (id) => api.get(`/api/video/${id}`),
  process: (url, level) => api.post('/api/process', { url, level }),
  delete: (id) => {
    cacheService.delete(`/api/video/${id}`);
    return api.delete(`/api/video/${id}`);
  }
};

// Question related APIs
export const questionAPI = {
  getByVideo: (videoId) => api.get(`/api/questions/${videoId}`),
  submitAnswer: (videoId, questionId, answer) => 
    api.post(`/api/questions/${videoId}/answer`, { questionId, answer }),
  getAudio: (audioPath) => `${API_BASE_URL}${audioPath}`
};

// Metrics and analytics
export const metricsAPI = {
  submitScore: (score, difficulty) => 
    api.post('/api/metrics/comprehension', { score, difficulty_level: difficulty }),
  getStats: () => api.get('/api/metrics/stats')
};