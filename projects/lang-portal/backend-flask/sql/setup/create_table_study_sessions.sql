CREATE TABLE IF NOT EXISTS study_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  group_id INTEGER NOT NULL,  -- The group of words being studied
  study_activity_id INTEGER NOT NULL,  -- The activity performed
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Timestamp of the session
  FOREIGN KEY (group_id) REFERENCES groups(id),
  FOREIGN KEY (study_activity_id) REFERENCES study_activities(id)
);