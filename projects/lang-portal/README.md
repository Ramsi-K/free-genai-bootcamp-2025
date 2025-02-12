# Lang Portal - Backend API

## 📌 Index

- [Overview](#overview)
- [Project Goals](#project-goals)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Diagrams](#diagrams)

## 📌 Overview

Lang Portal is a **backend API** for a **Korean language learning platform**, providing:

- A **vocabulary inventory** for learners
- A **Learning Record Store (LRS)** for tracking progress
- A **launchpad for study activities** like quizzes & flashcards

## 📌 Project Goals

- Develop a **SQLite-backed API** for managing study sessions & word groups
- Ensure API responses align with frontend needs
- Implement **study tracking & performance analytics**

## 📌 API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/api/words` | Fetch vocabulary words (paginated) |
| `GET` | `/api/groups` | Fetch groups (paginated) |
| `GET` | `/api/groups/:id` | Fetch words from a specific group |
| `POST` | `/api/study_sessions` | Create a new study session |
| `POST` | `/api/study_sessions/:id/review` | Submit a word review |

## 📌 Database Schema

- **`words`**: Stores Korean vocabulary words
- **`groups`**: Manages word collections
- **`word_groups`**: Many-to-many relationship between words & groups
- **`study_sessions`**: Records learning sessions
- **`word_review_items`**: Tracks correctness of word reviews

## 📌 Diagrams

- **Entity-Relationship Diagram**  
  *(./diagrams/lang_portal_erd.mmd)*  

- **System Architecture Diagram**  
  *(./diagrams/lang_portal_system_architecture.mmd)*  

- **Component Diagram**  
  *(./diagrams/lang_portal_component_diagram.mmd)*  

- **API Flow Diagram**  
  *(./diagrams/lang_portal_api_flow.mmd)*  

- **Deployment Architecture Diagram**  
  *(./diagrams/lang_portal_deployment_architecture.mmd)*  
