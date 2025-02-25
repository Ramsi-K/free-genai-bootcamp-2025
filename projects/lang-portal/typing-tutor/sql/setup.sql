-- This is the words
CREATE TABLE words (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kanji TEXT NOT NULL,
  romaji TEXT NOT NULL,
  english TEXT NOT NULL,
  parts JSON
);

CREATE TABLE groups {
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NULL NOLL
}

CREATE TABLE word_groups {
  word_id INTEGER NOT NULL,
  group_id INTEGER NOT NULL,
  FOREIGN KEY (word_id) REFERENCES words(id)
  FOREIGN KEY (group_id) REFERENCES groups(id)
}


-- This stores if someone got a word correct or wrong
CREATE TABLE word_reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  word_id INTEGER NOT NULL,
  FOREIGN KEY (word_id) REFERENCES words(id)
)