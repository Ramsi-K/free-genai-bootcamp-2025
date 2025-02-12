CREATE TABLE IF NOT EXISTS word_review_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  word_id INTEGER NOT NULL,
  study_session_id INTEGER NOT NULL,  -- Link to study session
  correct BOOLEAN NOT NULL,  -- Whether the answer was correct (true) or wrong (false)
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Timestamp of the review
  FOREIGN KEY (word_id) REFERENCES words(id),
  FOREIGN KEY (study_session_id) REFERENCES study_sessions(id)
);