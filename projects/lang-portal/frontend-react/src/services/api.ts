const API_BASE_URL = 'http://localhost:5000';

// Group types
export interface Group {
  id: number;
  group_name: string;
  word_count: number;
}

export interface GroupsResponse {
  groups: Group[];
  total_pages: number;
  current_page: number;
}

// Word types
export interface WordGroup {
  id: number;
  name: string;
}

export interface Word {
  id: number;
  kanji: string;
  romaji: string;
  english: string;
  correct_count: number;
  wrong_count: number;
  groups: WordGroup[];
}

export interface WordResponse {
  word: Word;
}

export interface WordsResponse {
  words: Word[];
  total_pages: number;
  current_page: number;
  total_words: number;
}

// Study Session types
export interface StudySession {
  id: number;
  group_id: number;
  group_name: string;
  activity_id: number;
  activity_name: string;
  start_time: string;
  end_time: string;
  review_items_count: number;
}

export interface WordReview {
  word_id: number;
  is_correct: boolean;
}

// Dashboard types
export interface RecentSession {
  id: number;
  group_id: number;
  activity_name: string;
  created_at: string;
  correct_count: number;
  wrong_count: number;
}

export interface StudyStats {
  total_vocabulary: number;
  total_words_studied: number;
  mastered_words: number;
  success_rate: number;
  total_sessions: number;
  active_groups: number;
  current_streak: number;
}

// Group API
export const fetchGroups = async (
  page: number = 1,
  sortBy: string = 'name',
  order: 'asc' | 'desc' = 'asc'
): Promise<GroupsResponse> => {
  const response = await fetch(
    `${API_BASE_URL}/groups?page=${page}&sort_by=${sortBy}&order=${order}`
  );
  if (!response.ok) {
    throw new Error('Failed to fetch groups');
  }
  return response.json();
};

export interface GroupDetails {
  id: number;
  group_name: string;
  word_count: number;
}

export interface GroupWordsResponse {
  words: Word[];
  total_pages: number;
  current_page: number;
}

export const fetchGroupDetails = async (
  groupId: number,
  page: number = 1,
  sortBy: string = 'kanji',
  order: 'asc' | 'desc' = 'asc'
): Promise<GroupDetails> => {
  const response = await fetch(`${API_BASE_URL}/groups/${groupId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch group details');
  }
  return response.json();
};

export const fetchGroupWords = async (
  groupId: number,
  page: number = 1,
  sortBy: string = 'kanji',
  order: 'asc' | 'desc' = 'asc'
): Promise<GroupWordsResponse> => {
  const response = await fetch(
    `${API_BASE_URL}/groups/${groupId}/words?page=${page}&sort_by=${sortBy}&order=${order}`
  );
  if (!response.ok) {
    throw new Error('Failed to fetch group words');
  }
  return response.json();
};

// Word API
export const fetchWords = async (
  page: number = 1,
  sortBy: string = 'kanji',
  order: 'asc' | 'desc' = 'asc'
): Promise<WordsResponse> => {
  const response = await fetch(
    `${API_BASE_URL}/words?page=${page}&sort_by=${sortBy}&order=${order}`
  );
  if (!response.ok) {
    throw new Error('Failed to fetch words');
  }
  return response.json();
};

export const fetchWordDetails = async (wordId: number): Promise<Word> => {
  const response = await fetch(`${API_BASE_URL}/words/${wordId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch word details');
  }
  const data: WordResponse = await response.json();
  return data.word;
};

// Study Session API
export const createStudySession = async (
  groupId: number,
  studyActivityId: number
): Promise<{ session_id: number }> => {
  const response = await fetch(`${API_BASE_URL}/study_sessions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      group_id: groupId,
      study_activity_id: studyActivityId,
    }),
  });
  if (!response.ok) {
    throw new Error('Failed to create study session');
  }
  return response.json();
};

export const submitStudySessionReview = async (
  sessionId: number,
  reviews: WordReview[]
): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/study_sessions/${sessionId}/review`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ reviews }),
  });
  if (!response.ok) {
    throw new Error('Failed to submit study session review');
  }
};

export interface StudySessionsResponse {
  items: StudySession[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export async function fetchStudySessions(
  page: number = 1,
  perPage: number = 10
): Promise<StudySessionsResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/study-sessions?page=${page}&per_page=${perPage}`
  );
  if (!response.ok) {
    throw new Error('Failed to fetch study sessions');
  }
  return response.json();
}

export interface StudySessionsResponse {
  study_sessions: StudySession[];
  total_pages: number;
  current_page: number;
}

export async function fetchGroupStudySessions(
  groupId: number,
  page: number = 1,
  sortBy: string = 'created_at',
  order: 'asc' | 'desc' = 'desc'
): Promise<StudySessionsResponse> {
  const response = await fetch(
    `${API_BASE_URL}/groups/${groupId}/study_sessions?page=${page}&sort_by=${sortBy}&order=${order}`
  );
  if (!response.ok) {
    throw new Error('Failed to fetch group study sessions');
  }
  return response.json();
}

// Dashboard API
export const fetchRecentStudySession = async (): Promise<RecentSession | null> => {
  const response = await fetch(`${API_BASE_URL}/dashboard/recent-session`);
  if (!response.ok) {
    throw new Error('Failed to fetch recent session');
  }
  const data = await response.json();
  console.log('Raw response from recent session:', data);
  return data;
};

export const fetchStudyStats = async (): Promise<StudyStats> => {
  const response = await fetch(`${API_BASE_URL}/dashboard/stats`);
  if (!response.ok) {
    throw new Error('Failed to fetch study stats');
  }
  return response.json();
};
