# HagXwon Game Design & Technical Specifications

## Overview

### App Concept

A Korean language learning web application using interactive AI-powered agents to deliver dynamic, personalized, and emotionally engaging educational content. The system supports multiple personalities (AhjummaGPT, AhjussiGPT, KoreabooGPT), agent-based services (Flashcard Agent, Listening Agent, Story Agent, MUD Game Agent, Noraebang Agent), and a vector database for Retrieval-Augmented Generation (RAG).

### Target Audience

- Korean language learners (beginner to intermediate)
- Users interested in immersive or gamified learning experiences

### Platform

- Web-based interface
- Backend using FastAPI
- Frontend using Jinja2 (minimal, mobile-friendly)
- LLMs accessed via Ollama or Hugging Face

## Core Agents

### 1. Flashcard Agent (Core)

- Role: Vocabulary review and spaced repetition
- Features: Uses RAG to inject examples; sass/personality layered on output

### 2. Listening Agent (Core)

- Role: Respond to uploaded audio, speech-to-text (ASR), evaluate
- Features: Agent responds with feedback based on transcription quality

### 3. Story Agent (Core)

- Role: Generate language learning stories
- Features: Personalized story generation + translation + image support

### 4. MUD Game Agent (Core)

- Role: Text adventure game with embedded vocabulary & grammar goals
- Features: Branching choices, immersive scenes, vocabulary gating

### 5. Noraebang Agent (Stretch)

- Role: Interactive singing + vocabulary breakdowns from lyrics
- Features: Pulls Korean song, analyzes lyrics, quizzes user

### 6. Object Detection Agent (Stretch)

- Role: Mobile camera input → live object labeling in Korean
- Features: Uses YOLO/MediaPipe and returns translated labels in real time

## Personas (Personalities)

### AhjummaGPT

- Description: Judgmental, emotionally blunt Korean auntie
- Speech Style: Sarcastic, passive-aggressive, old-fashioned

### AhjussiGPT

- Description: Rambly Korean uncle who gives strange analogies
- Speech Style: Mix of casual and outdated Korean

### KoreabooGPT

- Description: Overexcited K-pop fan, uses awkward formality
- Speech Style: K-drama clichés, enthusiastic code-switching

## Story Framework (MUD Agent / Visual Novel)

- Linear scenes with key decision points
- Character-driven interactions in locations (e.g., 학원, 시장, 카페)
- Designed to teach one Korean phrase or structure per scene
- Each choice tied to vocabulary + grammar usage

## Vector DB / RAG System

- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- Vector DB: ChromaDB (mounted volume or HF-hosted)
- Used by Flashcard, Listening, and Story Agents to inject real examples

## Tech Stack

- **Backend**: FastAPI
- **Frontend**: Jinja2 Templates + CSS (mobile-first)
- **Vector DB**: ChromaDB (or FAISS)
- **LLM Interface**: Ollama (locally) + optional fallback to OpenAI
- **Fine-Tuning**: QLoRA + DeepSeek / Llama3

## Architecture Overview

See `README.md` for Mermaid diagram and core/stretched delivery plan.
