CREATE TABLE IF NOT EXISTS word_groups (
  word_id INTEGER NOT NULL,
  group_id INTEGER NOT NULL,
  FOREIGN KEY (word_id) REFERENCES words(id),
  FOREIGN KEY (group_id) REFERENCES groups(id)
);