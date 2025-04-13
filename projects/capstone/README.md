> Note: WIP

# Capstone Project - HagXwon

## 📦 Project Overview

HagXwon is an AI-powered Korean language learning app built for the GenAI Bootcamp. It features multiple AI agents (Flashcard, Listening, Story, MUD) and fine-tuned personalities (AhjummaGPT, AhjussiGPT, KoreabooGPT). Users engage with the language through sassy tutoring, branching narratives, object recognition, and karaoke-inspired practice.

## 🧠 Core Features (Must Deliver)

- ✅ Flashcard Agent with RAG support
- ✅ Listening Agent for TTS/ASR evaluation
- ✅ Story Agent with image support (optional fallback to static images)
- ✅ MUD Game Agent (text-based branching logic)
- ✅ AhjummaGPT personality with fine-tuned model or prompt injection
- ✅ Basic frontend connected to FastAPI backend
- ✅ RAG pipeline with ChromaDB and embedded vocab
- ✅ Dockerized, runnable end-to-end app

## 🌟 Stretch Goals (Time Permitting)

- Noraebang Agent (Lyrics-based quiz/singing)
- Object Detection Agent (camera input → live labels)
- AhjussiGPT and KoreabooGPT fine-tuned models
- UI polish (dropdown tutor selector, animated feedback)
- Hugging Face-hosted prompt templates + vector data

## 🕰️ Tentative Delivery Schedule

```mermaid
gantt
title HagXwon Build Timeline
    dateFormat  YYYY-MM-DD
    section Planning
    Finalize specs and MVP          :done,    plan1, 2025-03-26, 1d
    Finish bootcamp lectures        :active,  plan2, 2025-03-26, 1d

    section Core Build
    Flashcard Agent (RAG)           :         build1, 2025-03-27, 2d
    Listening Agent                 :         build2, 2025-03-29, 2d
    Story Agent                     :         build3, 2025-03-31, 1d
    MUD Agent core logic            :         build4, 2025-04-01, 2d

    section Personality Fine-Tuning
    AhjummaGPT dataset + LoRA       :         ftune1, 2025-03-27, 2d
    Inference integration           :         ftune2, 2025-03-29, 1d

    section UI & Integration
    Frontend wiring (Jinja2)        :         ui1,    2025-04-02, 2d
    Dockerization + HF asset setup :         ship1,  2025-04-04, 1d

    section Stretch Goals
    KoreabooGPT, AhjussiGPT         :         opt1,   2025-04-05, 2d
    Noraebang Agent                 :         opt2,   2025-04-07, 2d
    Object Detection Agent          :         opt3,   2025-04-09, 2d

    section Final Polish
    Testing + Debugging             :         polish1,2025-04-10, 1d
    Final video + README            :         polish2,2025-04-11, 1d
    Final Submission                :         deadline,2025-04-12, 1d
```

## 🧩 Architecture Diagram (High-Level)

```mermaid
graph TD
  UI[User Interface] -->|POST /flashcard| FastAPI
  UI -->|POST /story| FastAPI
  UI -->|POST /listen| FastAPI
  FastAPI -->|Query| ChromaDB
  FastAPI -->|Call| OllamaLLM[AhjummaGPT (via Ollama)]
  FastAPI -->|Load| PromptTemplates[Prompt Templates / HF-hosted]
  ChromaDB -->|Results| FastAPI
  OllamaLLM -->|Response| FastAPI
  FastAPI --> UI
```

## 📁 File Structure (TBD)

```text
project-root/
├── app/
│   ├── main.py
│   ├── agents/
│   ├── prompts/
│   └── templates/
├── rag/
│   └── chromadb_data/
├── data/
│   └── vocab.json
├── Dockerfile
├── docker-compose.yml
├── README.md
├── TechSpecs.md
├── Characters.md
└── MUDGameScript.md
```

```text
hagxwon-capstone/
├── README.md
├── tech-specs/
│   ├── hagxwon-system-architecture.md
│   ├── character-personas.md
│   ├── delivery-gantt.md
│   └── fine-tuning-strategy.md
├── backend/
│   ├── app/
│   └── Dockerfile
├── frontend/
│   ├── templates/
│   └── static/
├── data/
│   ├── vector-db-sources/
│   └── persona-finetuning/
├── journal/
│   ├── 2025-03-25_26.md
├── diagrams/
│   └── napkin-ai/
└── scratchpad/
```

## ✅ To-Do Summary

- [x] Write Tech Specs & Persona Doc
- [ ] Finish lectures
- [ ] Build core agents
- [ ] Run AhjummaGPT LoRA fine-tune
- [ ] Setup RAG (ChromaDB + HF assets)
- [ ] Build MVP UI
- [ ] Dockerize and write final demo script

You’ve got this. Let’s ship it clean. 🚀
