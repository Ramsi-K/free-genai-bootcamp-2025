CREATE TABLE IF NOT EXISTS study_activities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,  -- Name of the activity (e.g., "Flashcards", "Quiz")
  url TEXT NOT NULL,  -- The full url of the study activity
  preview_url TEXT    -- The url to the preview image for the activity
);