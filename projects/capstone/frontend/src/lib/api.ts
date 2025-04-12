const API_URL = import.meta.env.VITE_API_URL;

console.log('API URL:', API_URL); // Debug API URL

export const api = {
  // Dashboard
  getDashboardStats: () => fetch(`${API_URL}/dashboard/quick-stats`).then(res => res.json()),
  getLastStudySession: () => fetch(`${API_URL}/dashboard/last_study_session`).then(res => res.json()),
  getStudyProgress: () => fetch(`${API_URL}/dashboard/study_progress`).then(res => res.json()),

  // Words
  getWords: (page = 1) => fetch(`${API_URL}/words?skip=${(page-1)*100}&limit=100`).then(res => res.json()),
  getWord: (id: number) => fetch(`${API_URL}/words/${id}`).then(res => res.json()),

  // Groups
  getGroups: async (type?: 'pos' | 'theme') => {
    try {
      const params = new URLSearchParams({
        group_type: type || 'theme',
        skip: '0',
        limit: '100'
      });

      const url = `${API_URL}/groups?${params}`;
      console.log('Fetching groups from:', url);

      const response = await fetch(url);
      const data = await response.json();
      console.log('Raw groups from API:', data);
      return data; // Just return exactly what the API gives us
    } catch (error) {
      console.error('Groups API call failed:', error);
      throw error;
    }
  },
  getGroup: (id: number) => fetch(`${API_URL}/groups/${id}`).then(res => res.json()),
  getGroupWords: async (id: number) => {
    try {
      const response = await fetch(`${API_URL}/groups/${id}/words`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Group words response:', data);
      return data;
    } catch (error) {
      console.error('Failed to fetch group words:', error);
      throw error;
    }
  },
  getGroupSessions: (id: number) => fetch(`${API_URL}/groups/${id}/study_sessions`).then(res => res.json()),

  // Study Sessions
  createStudySession: (groupId: number, activityId: number) => 
    fetch(`${API_URL}/study_sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ group_id: groupId, study_activity_id: activityId })
    }).then(res => res.json()),

  submitWordReview: (sessionId: number, wordId: number, correct: boolean) =>
    fetch(`${API_URL}/study_sessions/${sessionId}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ word_id: wordId, correct })
    }).then(res => res.json()),

  // Study Activities
  getStudyActivities: () => fetch(`${API_URL}/study_activities`).then(res => res.json()),
  getStudyActivity: (id: number) => fetch(`${API_URL}/study_activities/${id}`).then(res => res.json()),

  // Admin
  resetHistory: () => 
    fetch(`${API_URL}/admin/reset_history`, { method: 'POST' }).then(res => res.json()),
  resetDatabase: () => 
    fetch(`${API_URL}/admin/full_reset`, { method: 'POST' }).then(res => res.json())
};
