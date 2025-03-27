# HagXwon Capstone: Unified System & Deployment Specification

This is the master spec document for the HagXwon GenAI Bootcamp Capstone Project.
It merges all backend, frontend, data, agent, and deployment specs into one coherent system architecture.

---

## 1. Project Summary

**HagXwon** is an AI-powered Korean language tutor app featuring modular training agents (AhjummaGPT, AhjussiGPT, etc.), flashcards, grammar-aware dialogue, handwriting feedback, and cultural insights — powered by RAG and optional fine-tuning.

The project balances fast prototyping with clean architectural principles, inspired by OPEA but optimized for solo-dev velocity.

---

## 2. System Architecture Overview

### 2.1 Backend

- Framework: **FastAPI**
- Structure:
  - `agents/` folder contains separate agents (Flashcard, Tutor, MUD, etc.)
  - Shared `utils/` folder for prompts, chunking, retrieval, etc.
  - RAG modules live in `rag/`

### 2.2 Frontend

- Framework: Flask + Jinja templates
- Connects to backend via REST APIs
- Responsive UI with persona-select, chat, flashcards, etc.

### 2.3 Database

- **Relational DB** (SQLite or Supabase): user info, progress, vocab history
- **Vector DB** (ChromaDB): Korean content, grammar rules, culture materials

### 2.4 Infrastructure

- **Dockerized** for deployment
- Optional multi-container setup with Ollama or embedding microservices
- Deployment via Docker Compose

---

## 3. Data Ingestion Pipeline

### 3.1 Raw Data Sources

- Open-source Korean textbooks (PDF)
- Grammar guides, vocab lists
- Cultural content and culinary references

### 3.2 Preprocessing Flow

- PDFs → Text via `PyMuPDF` or OCR (`pytesseract`)
- Text → Cleaned & chunked
- Chunked text saved to `/data/processed/`

### 3.3 Embedding

- Model: Ollama (e.g., `mxbai-embed-large`) or SentenceTransformers
- Storage: ChromaDB
- Metadata includes:
  - `source_type` (grammar, food, dialogue)
  - `TOPIK_level`
  - `persona_affinity` (e.g., Ahjumma = food, Ahjussi = proverbs)

### 3.4 Optional Upload

- Export full dataset to Hugging Face for reproducibility

---

## 4. RAG Retrieval System

### 4.1 Per-Agent Access

Each agent has access to:

- A shared or dedicated Chroma collection
- Prompt templates scoped to persona tone and logic

### 4.2 Retrieval Flow

- User input → parsed intent → relevant chunk retrieved → injected into persona prompt → sent to LLM

---

## 5. Fine-Tuning Spec

### 5.1 Format (JSONL)

Each sample:

```json
{
  "persona": "AhjummaGPT",
  "tone": "roast",
  "TOPIK_level": 2,
  "input": "You forgot to add the object marker again.",
  "response": "Tsk. What are you, a tourist? Go back and fix it."
}
```

### 5.2 Training Plan

- QLoRA-based fine-tuning on quantized DeepSeek or Polyglot-Ko models
- Each persona: 300–1000 samples
- Prioritize AhjummaGPT
- Train on Kaggle or local GPU

### 5.3 Alternatives

- If fine-tuning not feasible in time, use prompt-injected style simulation

---

## 6. Backend Modules

```
backend/
├── main.py
├── agents/
│   ├── flashcards.py
│   ├── ahjumma.py
│   ├── mud_game.py
├── rag/
│   ├── embed.py
│   ├── retrieve.py
├── utils/
│   ├── prompt_templates.py
│   ├── pdf_to_text.py
├── db/
│   ├── schema.sql
│   └── user_data.py
```

---

## 7. Deployment Plan

### 7.1 Simple (Recommended)

- One Docker container for FastAPI backend
- ChromaDB and Ollama optionally in Docker Compose

### 7.2 Modular (Optional)

- Split Flashcard Agent, RAG Embedder, and Tutor logic into microservices
- Follow lightweight OPEA-style structure if time allows

### 7.3 Docker Compose

- Backend
- ChromaDB
- Ollama (optional)

---

## 8. Personas & Prompt Structure

| Persona     | Role                      | Specialty           |
| ----------- | ------------------------- | ------------------- |
| AhjummaGPT  | Judgy Korean Auntie       | Food, grammar, sass |
| AhjussiGPT  | Retired uncle             | Proverbs, slang     |
| KoreabooGPT | Over-enthusiastic learner | K-pop, exclamations |
| SunbaeGPT   | Supportive senior student | Grammar help        |

Each uses distinct prompt templates and tones. Retrieval is filtered by `persona_affinity`.

---

## 9. Stretch Goals

- Noraebang lyric translation game
- Real-time webcam object labeling (Korean)
- Sentence writing practice + Ahjumma roasts
- SadTalker + GPT-SoVITS avatar video

---

## 10. Gantt-style Build Plan (T-minus Countdown)

| Week | Focus                                   |
| ---- | --------------------------------------- |
| T–16 | Finalize spec, start backend structure  |
| T–15 | Backend running, convert PDFs to text   |
| T–14 | Chunk + embed, start RAG integration    |
| T–13 | Flashcard + Tutor agents working        |
| T–12 | Fine-tuning or persona prompt templates |
| T–11 | Frontend endpoints + Docker setup       |
| T–10 | Avatar, extras, polish + README         |

---

This spec will be updated and versioned as components are completed.
Let’s go. 🚀
