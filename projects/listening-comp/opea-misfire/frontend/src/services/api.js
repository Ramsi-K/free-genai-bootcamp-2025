import axios from 'axios';

const MEGA_SERVICE_URL = process.env.REACT_APP_MEGA_SERVICE_URL || 'http://localhost:8000';
const METRICS_URL = process.env.REACT_APP_METRICS_URL || 'http://localhost:9090';

// ...existing code...

export const submitComprehensionScore = async (score, difficulty) => {
  try {
    await axios.post(`${MEGA_SERVICE_URL}/api/metrics/comprehension`, {
      score,
      difficulty_level: difficulty
    });
  } catch (error) {
    console.error('Error submitting comprehension score:', error);
  }
};

export const getServiceMetrics = async () => {
  try {
    const response = await axios.get(`${METRICS_URL}/api/v1/query`, {
      params: {
        query: 'korean_questions_total'
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching metrics:', error);
    return null;
  }
};

// ...existing code...