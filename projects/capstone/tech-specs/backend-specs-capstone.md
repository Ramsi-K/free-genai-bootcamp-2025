# 🧠 Backend Server Technical Specs: Python + FastAPI (Korean)

This document outlines the backend architecture and implementation strategy for the HagXwon language learning platform, built using **Python** and **FastAPI**. It supports a modular multi-agent AI tutor system focused on Korean language acquisition.

---

## 🎯 Business Goal

To create a trauma-informed, sass-powered learning portal that supports:

- **Vocabulary Flashcards** with feedback
- **Chat-based Tutoring** (AhjummaGPT)
- **Listening Practice**
- **MUD Game-based Learning**
- **Live Object Recognition** (camera-based)
- **Customizable AI Personas** for immersive Korean learning

---

## 🧰 Technical Requirements

- **Framework**: FastAPI (Python)
- **Serving**: Uvicorn with hot-reload for dev
- **API Format**: REST (JSON responses only)
- **Authentication**: None (single-user assumption)
- **Database**: In-memory for dev; SQLite/Postgres planned
- **LLM Backend**: DeepSeek or similar via local model (vLLM/Ollama)
- **Frontend Access**: Swagger UI for testing, browser frontend later
- **Modularity**: Agents are separate files/services (multi-agent ready)

---

## 📂 Directory Structure

```plaintext
/backend
  ├── main.py                # FastAPI app and base routes
  ├── agents/
  │   ├── chat.py           # AhjummaGPT logic
  │   ├── flashcards.py     # Flashcard logic
  │   ├── listening.py      # Listening practice logic
  │   ├── mud.py            # MUD game interface
  │   └── object_detect.py  # Live object recognition logic
  ├── models.py             # DB Models (future)
  ├── data/
  │   └── flashcard.json     # Optional static vocab data
  └── utils.py              # Shared helper functions
```

---

## 📚 Core API Endpoints (Current + Planned)

### ✅ Flashcards

- `GET /flashcards` → Get a random flashcard
- `POST /flashcards/attempt` → Submit answer and get sass

### 🩴 Chat (AhjummaGPT)

- `POST /chat` → Submit message, get sarcastic feedback

### 🎧 Listening Practice

- `GET /listening/start` → Start a listening session
- `POST /listening/attempt` → Submit answers

### 📖 Storybook (Future)

- `GET /storybook/generate` → Generate bilingual short story

### 🎮 MUD Game (Future)

- `GET /mud/start` → Begin text-based adventure
- `POST /mud/action` → Perform action (e.g., move, talk, fight)

### 🤳 Object Detection (Future)

- `POST /vision/scan` → Submit image from phone/webcam
- `GET /vision/label-map` → Map COCO labels to Korean words

---

## 🧠 LLM Integration

| Component         | Method                                      |
| ----------------- | ------------------------------------------- |
| Chat agent        | Static prompt OR LoRA fine-tune (DeepSeek)  |
| Reasoning         | Handled via local inference (vLLM / Ollama) |
| Persona injection | Prompt templates (Ahjumma, Halmeoni, etc.)  |
| API calls         | Planned via Toolformer-style agent chaining |

---

## 🐳 Docker & Deployment

- Dockerfile will include:
  - Python environment
  - FastAPI app
  - Local model or API endpoint
- Future deployment via:
  - Render / Fly.io / Railway
  - Domain management via Name.com
- Mobile access via LAN IP or hosted HTTPS domain

---

## 🧪 Swagger UI

Available at `http://127.0.0.1:8000/docs` when running locally. Provides:

- Interactive test interface for all endpoints
- Schema validation for request/response bodies

---

## ✨ Future Features

- Study session tracking
- Korean-English bilingual storybooks
- Listening-to-vocab pipeline
- AI-based tutoring through quiz and explanation
- Camera-based object name overlay in Korean

---

## 🛠️ Run Locally

```bash
uvicorn main:app --reload
```

Then visit: `http://127.0.0.1:8000/docs`

---
