# 🚀 FastAPI Vibe Guide – For Ramsi

from fastapi import FastAPI, Request
from pydantic import BaseModel
import random

app = FastAPI()

# Temporary in-memory store for the last flashcard
last_flashcard = {}


# 👋 BASIC ROUTE
@app.get("/")
def home():
    return {"message": "Welcome to HagXwon Terminal. Type wisely."}


# 🧠 SIMPLE GET ENDPOINT
@app.get("/hello")
def say_hello():
    return {"message": "Annyeong! You look tired. Study anyway."}


# 💬 CHAT ENDPOINT – You POST, tutor replies
class Message(BaseModel):
    message: str


@app.post("/chat")
def talk_to_tutor(msg: Message):
    prompt = msg.message
    reply = f"You said: '{prompt}'. That's cute. WRONG. Do it again."
    return {"tutor_reply": reply}


# 📚 FAKE WORD PRACTICE (GET)
@app.get("/word")
def get_word():
    return {"hangul": "학교", "romanization": "hakgyo", "meaning": "school"}


# ✅ RECORD CORRECT ATTEMPT (POST)
@app.post("/word/correct")
def correct_word():
    return {"message": "Fine. You got ONE right. Congratulations, genius."}


# ❌ RECORD INCORRECT ATTEMPT (POST)
@app.post("/word/incorrect")
def wrong_word():
    return {"message": "Nope. That was wrong. Again. Slower this time."}


# 🔁 FLASHCARD SHUFFLE MOCK
mock_flashcards = [
    {
        "id": "w001",
        "hangul": "사과",
        "romanization": "sagwa",
        "meaning": "apple",
    },
    {"id": "w002", "hangul": "물", "romanization": "mul", "meaning": "water"},
    {
        "id": "w003",
        "hangul": "책상",
        "romanization": "chaeksang",
        "meaning": "desk",
    },
    {
        "id": "w004",
        "hangul": "창문",
        "romanization": "changmun",
        "meaning": "window",
    },
    {
        "id": "w005",
        "hangul": "의자",
        "romanization": "uija",
        "meaning": "chair",
    },
]


@app.get("/flashcards")
def get_flashcard():
    shuffled = mock_flashcards.copy()
    random.shuffle(shuffled)
    flashcard = shuffled[0]
    last_flashcard["current"] = flashcard
    return {"flashcard": flashcard}


class FlashcardAttempt(BaseModel):
    user_answer: str


@app.post("/flashcards/attempt")
def evaluate_flashcard(attempt: FlashcardAttempt):
    card = last_flashcard.get("current")
    if not card:
        return {"error": "No flashcard has been served yet."}

    correct = card["meaning"].strip().lower()
    user = attempt.user_answer.strip().lower()

    if user == correct:
        return {"result": "correct", "message": "You live... for now."}
    else:
        return {
            "result": "incorrect",
            "message": f"Wrong. It's '{card['meaning']}'. Try again.",
        }


# 🛠️ RUN THIS LOCALLY:
# Run with: uvicorn fastapi-practice-main:app --reload
# Visit http://127.0.0.1:8000/docs for auto Swagger UI
