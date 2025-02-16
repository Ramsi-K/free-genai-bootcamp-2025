CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hangul TEXT,  -- ✅ Replaces kanji
    romanization TEXT,  -- ✅ Replaces romaji
    english TEXT,
    parts JSON,
    example_korean TEXT,  -- ✅ New column
    example_english TEXT  -- ✅ New column
);
