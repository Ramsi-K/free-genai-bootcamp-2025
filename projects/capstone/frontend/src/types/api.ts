export interface Word {
  hangul: string;
  romanization: string;
  english: string[];
}

export interface Group {
  id: number;
  name: string;
  words_count: number;
  group_type: string;
}

export type WordGroup = Group;

export interface StudySession {
  id: number;
  group_id: number;
  study_activity_id: number;
  created_at: string;
}

export interface StudyActivity {
  id: number;
  name: string;
  url: string;
  thumbnail_url?: string;
  created_at: string;
}

export interface DashboardStats {
  total_words: number;
  total_groups: number;
  total_sessions: number;
}

export interface StudyProgress {
  correct: number;
  incorrect: number;
}
