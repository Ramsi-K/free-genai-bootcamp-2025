# HagXwon: AI-Powered English & Korean Learning for Korea’s Hagwon Industry

## 📂 Project Directory Structure

```
📂 project-1-architecting-genai/
│── 📜 README.md                 # High-level overview, links to details
│── 📂 docs/                      # Documentation
│   │── 📜 business-case.md       # Business case & background story
│   │── 📜 business-proposal.md   # Business execution strategy
│   │── 📜 project-requirements.md # Bootcamp project description & requirements
│   │── 📜 togaf-compliance.md    # TOGAF compliance tracking
│   │── 📜 togaf-ai-mapping.md    # TOGAF AI translation & system mapping
│   │── 📜 architecture-strategy.md [TODO]  # Technical architecture & system design (planned)
│   │── 📜 deployment-strategy.md [TODO]  # Deployment, CI/CD, risk management (planned)
│   │── 📜 conceptual-design.md   # High-level conceptual system architecture
│   │── 📜 system-design.md [TODO]  # Logical & Physical breakdown (planned)
│── 📂 diagrams/                   # Architecture & system design diagrams
│   │── 📜 enterprise-architecture.mmd  # Mermaid diagram (conceptual)
│   │── 📜 system-design.png [TODO]  # High-level system architecture (planned)
│   │── 📜 deployment-flow.mmd [TODO]  # Deployment pipeline (planned)
│   │── 📜 business-architecture.png  # Business architecture diagram
│   │── 📜 genai-architecture.png  # GenAI system architecture diagram
```

## 1. Overview

South Korea’s **hagwon (학원)** system is a **$20B+ industry**, yet traditional **rote-learning methods** limit students' real-world English proficiency.

**HagXwon** is an **AI-driven language learning platform** designed to enhance **English & Korean** education in hagwons by leveraging **interactive AI tutors, speech recognition, and adaptive learning**.

### Key Focus Areas

- **Korean-to-English & English-to-Korean**   (not just one-way learning)  
- **AI-powered speaking & pronunciation training**   for real-world fluency  
- **Adaptive AI tutors**   that reduce teacher workload & improve engagement  
- **Integration with hagwon LMS & management platforms**  
- **PIPA-compliant security & student data protection**

---

## 2. Project Requirements

This project follows the **GenAI Architecting Bootcamp** specifications. The goal is to create architectural diagrams that serve as **teaching aids** to help stakeholders understand key components of **GenAI workloads**. These diagrams aim to:

- **Visualize technical paths** and uncertainties when adopting AI.
- **Encourage discussions** around infrastructure choices, integration patterns, and system dependencies.
- **Follow structured architecture methodologies**, such as **TOGAF, C4 Model, and conceptual/logical/physical design approaches**.

For full details, see **[docs/project-requirements.md](docs/project-requirements.md)**.

## 3. Business Case

### 📊 The Korean Hagwon Industry: A $20B+ Market

- **$20.6 billion USD** spent annually on hagwon education.
- **70,000+ hagwons** operate across Korea, enrolling millions.
- **English proficiency is a priority**, but test-driven methods fail to build fluency.

### 🌍 The Global Demand for Learning Korean

- **15M+ people worldwide** are actively learning Korean.
- Korean is the **7th most learned language globally** (Duolingo 2023).
- AI-driven language learning can bridge gaps in **access & personalization**.

📌 **More details in [docs/business-case.md](docs/business-case.md).**

---

## 4. System Architecture

### 🛠 TOGAF-Compliant AI Learning System

The system is built using **TOGAF's ADM framework**, ensuring structured **enterprise AI adoption** and scalability.

### 🏗 Core System Layers

- **Frontend**   – AI-powered student & teacher dashboards  
- **Backend**   – AI orchestration, speech recognition, and lesson adaptation  
- **AI Models**   – Multimodal LLMs for **bilingual sentence construction & conversation AI**  
- **Cloud & On-Prem Strategy**   – Balancing cost, performance, and security  

📌 **See full system details in [docs/conceptual-design.md](docs/conceptual-design.md).**

---

## 5. AI-Powered Learning Features

- **AI Speech Coach**   – Pronunciation & fluency evaluation  
- **Live Conversational AI**   – Real-time adaptive dialogues  
- **Sentence Builder**   – AI-guided bilingual sentence formation  
- **AI Homework Evaluator**   – Automated grading with teacher oversight  
- **Instructor Assistant (RAG-powered)**   – AI-assisted lesson planning & Q&A

📌 **Feature breakdown in [docs/conceptual-design.md](docs/conceptual-design.md).**

---

## 6. Implementation Strategy

###  Deployment Phases

- **MVP (Weeks 1-6):** AI Speech Coach & Sentence Builder.
- **Phase 2 (Weeks 7-12):** AI Live Conversations, Homework Evaluator.
- **Phase 3 (Weeks 13+):** Full **hagwon LMS integration**.

### CI/CD & Infrastructure

- **Automated Testing & Deployment:**   CI/CD pipelines  
- **Infrastructure as Code:**   Terraform & Kubernetes  
- **Performance Monitoring:**   Real-time tracking with observability tools  

📌 **More in [docs/deployment-strategy.md](docs/deployment-strategy.md) [TODO].**

---

## 7. Security & Compliance

🔒 **Zero Trust Security Model**   – Strict access controls & role-based permissions  
📜 **PIPA Compliance**   – Adhering to Korea’s data privacy regulations  
✔ **AI Ethics & Governance**   – Bias mitigation, explainability, & fairness  

📌 **More in [docs/security-governance.md](docs/security-governance.md) [TODO].**

---

## 8. Enterprise Architecture & TOGAF Compliance

This project follows **TOGAF principles** for structured AI deployment.

### 📊 Architecture Diagram Levels

1. **Conceptual** – High-level system overview for stakeholders
2. **Logical** – AI components, workflows, and dependencies
3. **Physical** – Deployment details (cloud resources, infrastructure)

📌 **TOGAF tracking in [docs/togaf-compliance.md](docs/togaf-compliance.md).**

---

## 9. Next Steps & Roadmap

✔ **Week 0 Submission:** Conceptual Architecture Diagram  
🔜 **Week 1:** Logical Diagram & System Flow  
🔜 **Week 2+:** Physical Diagram, Infrastructure, & Deployment  

📌 **Live tracking in [roadmap.md](../../roadmap.md).**

---

## 10. References & Further Reading

- **[Bootcamp Project Description](docs/project-requirements.md)**
- **[Enterprise Architecture Diagrams](diagrams/)**
- **Duolingo Language Report 2023** (Korean as 7th most learned language globally).
- **Korean Hagwon Market Statistics 2023** ($20B+ industry, 70,000 hagwons).
- **TOGAF & C4 Model** – Structured AI adoption methodologies.

---
