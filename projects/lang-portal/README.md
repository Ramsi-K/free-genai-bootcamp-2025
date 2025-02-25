# Lang Portal – AI-Powered Language Learning Platform

This repository contains the **Lang Portal**, an AI-driven language learning platform designed to help users **study vocabulary, practice sentence construction, and track learning progress** through interactive sessions.

The project consists of **multiple backend implementations**, a provided frontend, and supporting documentation.

---

## **📌 Index**

- [Folder Structure](#-folder-structure)
- [Project Overview](#-project-overview)
- [Project Goals](#-project-goals)
- [Backend Implementations](#-backend-implementations)
- [Frontend (Instructor-Provided, To Be Extended)](#-frontend-instructor-provided-to-be-extended)
- [Typing Tutor](#-typing-tutor-instructor-provided)
- [Additional Projects (Probable Bootcamp Projects)](#-additional-projects-probable-bootcamp-projects)
- [Installation & Setup](#-installation--setup)
- [Testing & Debugging](#-testing--debugging)
- [Diagrams](#-click-for-diagrams)
- [Independent Research](#-independent-research)
- [Future Improvements](#-future-improvements)
- [Contributing](#-contributing)
- [License](#-license)

---

## **📂 Folder Structure**

```bash
lang-portal/
│── backend-go/         # Expanded backend (Go + Gin, 75% test coverage)
│── backend-fastapi/    # Placeholder for potential FastAPI implementation (not started)
│── backend-flask/      # Instructor-provided Flask backend (50% done, completed by me)
│── backend-backup/     # Archived first Go/Gin implementation (became too messy)
│── frontend-react/     # Instructor-provided frontend (100% implemented)
│── frontend/           # Empty frontend folder (may/may not be implemented)
│── typing-tutor/       # Instructor-provided typing tutor (may need modifications for Korean)
│── docs/               # Documentation (API specs, architecture)
│── diagrams/           # Architecture and data flow diagrams
│── README.md           # Project overview (this file)
```

---

## **🚀 Project Overview**

Lang Portal is designed to provide an **AI-powered learning experience**, enabling users to:

- **Practice vocabulary interactively**
- **Engage in structured study sessions**
- **Receive AI-generated sentence corrections and feedback**
- **Track study progress over time**

The project is built upon **multiple backend implementations** (Go, Flask), with **FastAPI as a potential future backend**, and includes a **prebuilt frontend provided by the instructors**, which will need to be extended for additional functionality.

---

## **📌 Project Goals**

- Develop a **SQLite-backed API** for managing study sessions & word groups
- Ensure API responses align with frontend needs
- Implement **study tracking & performance analytics**

---

## **🔹 Backend Implementations**

### **📌 Backend (Python - Flask) [Completed]**

- **Status:** ✅ **50% done by the instructor, completed by me**
- **Purpose:** Initial API required finishing remaining endpoints.
- **Time Spent:** Completed in a day.
- **Next Steps:** May transition to FastAPI depending on time and necessity.

### **📌 Backend (Python - FastAPI) [Planned, Not Started]**

- **Status:** 🟡 **Placeholder for possible transition from Flask**
- **Reason:** If time allows, FastAPI may be implemented for performance and maintainability.
- **Next Steps:** Focus remains on application and project implementations first.

### **📌 Backend (Go - Gin) [Expanded, but Not Final]**

- **Status:** ✅ **Self-implemented, expanded into a larger project**
- **Time Spent:** Initially planned for 2 days, became a 2-week project.
- **Challenges:** Feature creep added complexity beyond original scope.
- **Next Steps:** Likely **not viable** for final app due to frontend compatibility.

### **📌 Backend Decision**

- **Flask was completed and is being used for now.**
- **Go/Gin was an exploration but is not the final choice for deployment.**
- **FastAPI is a potential future transition but not a priority at this stage.**

---

## **🎨 Frontend (Instructor-Provided, To Be Extended)**

- **Status:** 🚧 **Prebuilt but not yet integrated with any backend.**
- **Provided by instructors** as a working UI.
- **Will need modifications to support additional features.**
- **Next Steps:** Integrate with Flask backend and extend for custom functionality.

---

## **⌨️ Typing Tutor (Instructor-Provided)**

- **Status:** ✅ **Fully implemented by the instructor**
- **Purpose:** Helps users practice typing skills.
- **Next Steps:** May need modifications to support Korean language input.

---

## **📜 Additional Projects (Probable Bootcamp Projects)**

- The following projects from the bootcamp **may be integrated into Lang Portal** based on available time:
  - **Multi-modal input (speech, handwriting recognition)**
  - **Personalized study plans based on AI-driven analytics**
  - **Adaptive difficulty adjustments for learning sessions**
  - **Expanded spaced repetition system for long-term retention**
  - **Automated lesson generation from web content**
- **Next Steps:** Evaluate time and feasibility for integrating these projects.

---

## **🔮 Future Improvements**

- [ ] **Finalize Flask Backend Implementation** (ensure full functionality)
- [ ] **Integrate Vector Database (FAISS/Pinecone) for Dynamic Word Retrieval**
- [ ] **Extend Provided Frontend for Custom Features**
- [ ] **Modify Typing Tutor to Support Korean**
- [ ] **Implement Model Context Protocol (MCP) for LLM Integration**
- [ ] **Enhance API capabilities with KR Dictionary and Grammar APIs**
- [ ] **Improve AI-driven personalization for adaptive study plans**
- [ ] **Evaluate FastAPI transition depending on project needs**

---

## **📝 Contributing**

Want to contribute? Check out our [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

## **📜 License**

This project is licensed under **CC BY-NC-SA 4.0** – see [LICENSE](LICENSE) for details.
