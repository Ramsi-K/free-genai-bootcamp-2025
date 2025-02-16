CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hangul TEXT NOT NULL,
    romanization TEXT NOT NULL,
    english TEXT NOT NULL,
    type TEXT NOT NULL,  -- ✅ Stores noun/verb/adjective
    parts TEXT NOT NULL,  -- ✅ Store JSON data as a string
    example_korean TEXT,  -- ✅ Stores example sentences in Korean
    example_english TEXT  -- ✅ Stores example sentences in English
);
