import json
from sqlmodel import Session
from src.api.words.models import WordModel
from src.db.session import engine

with open(
    "C:\\Users\\ramsi\\OneDrive\\Documents\\Github Projects\\gen-ai-bootcamp-2025\\projects\\capstone\\assets\\data\\processed\\korean_words_2000.json",
    "r",
    encoding="utf-8",
) as f:
    data = json.load(f)

with Session(engine) as session:
    for item in data:
        word = WordModel(**item)
        session.add(word)
    session.commit()

print("DB seeded.")
