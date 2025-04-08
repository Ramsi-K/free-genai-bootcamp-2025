import sqlite3

# Path to your database
db_path = "shared/data/app.db"

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insert data
cursor.execute(
    """
    INSERT INTO questions (video_id, question_text, audio_segment)
    VALUES (?, ?, ?)
""",
    (
        "test_video",
        "What is the capital of South Korea?",
        "Seoul is the capital of South Korea.",
    ),
)

# Commit and close
conn.commit()
conn.close()

print("Data inserted successfully!")
