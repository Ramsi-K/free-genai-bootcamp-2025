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

South Korea's **hagwon (학원)** system is the backbone of its private education sector, with parents collectively spending **over $20 billion USD annually** on after-school academies. The country has **over 70,000 hagwons**, enrolling millions of students each year. Despite this investment, many students spend **several hours daily in hagwons** yet struggle with **real-world English proficiency** due to traditional rote learning methods that emphasize test performance over practical application.

**HagXwon** is a next-generation, AI-powered platform designed to **enhance English and Korean language education** within Korea's hagwon industry. Our goal is to integrate **AI-driven interactive learning**, **personalized feedback**, and **real-time conversational AI** into the hagwon ecosystem to improve language fluency and engagement.

### **Key Focus Areas**

- **Korean-to-English & English-to-Korean Learning** (not just one direction)
- **Real-time AI-powered language coaching** for speaking, pronunciation, and grammar
- **Scalable & adaptive AI tutors** that reduce instructor workload
- **Integration with existing hagwon management systems**
- **PIPA-compliant data privacy and security** for student records

---

## 2. Project Requirements

This project follows the **GenAI Architecting Bootcamp** specifications. The goal is to create architectural diagrams that serve as **teaching aids** to help stakeholders understand key components of **GenAI workloads**. These diagrams aim to:

- **Visualize technical paths** and uncertainties when adopting AI.
- **Encourage discussions** around infrastructure choices, integration patterns, and system dependencies.
- **Follow structured architecture methodologies**, such as **TOGAF, C4 Model, and conceptual/logical/physical design approaches**.

For full details, see **[docs/project-requirements.md](docs/project-requirements.md)**.

---

## 3. System Architecture

### **TOGAF-Compliant AI Learning System**

The architecture follows **TOGAF’s ADM framework**, ensuring structured, enterprise-grade AI deployment.

### **Core System Layers**

- **Frontend:** responsive and scalable UI design
- **Backend:** strategies that align with scalability and performance goals
- **LLMs:** Evaluation of LLM models and machine translation technologies for optimizing bilingual learning
- **Speech Recognition:** and pronunciation evaluation tools that enhance speaking practice
- **Cloud & On-Prem Infrastructure:** balancing performance, cost, and security

For full system details, refer to **[docs/conceptual-design.md](docs/conceptual-design.md)**, which includes a **Mermaid-based architecture diagram**.

[TODO] A more detailed **system-design.md** (Logical + Physical breakdown) will be added later.

---

## 4. AI-Powered Learning Features

1. **AI Speaking Coach** – Pronunciation, fluency, and honorifics evaluation.  
2. **Live Conversation AI** – Real-time adaptive dialogue practice.  
3. **Sentence Builder** – AI guides students to form correct sentences without direct translation.  
4. **AI Homework Evaluator** – Automated scoring with instructor oversight.  
5. **Instructor Assistant (RAG-powered)** – AI-driven lesson planning and Q&A support.  

For feature breakdown, see **[docs/conceptual-design.md](docs/conceptual-design.md)**.

---

## 5. Implementation Strategy

### **🚀 Deployment Phases**

- **MVP (Weeks 1-6):** AI Speech Coach & Sentence Builder.
- **Phase 2 (Weeks 7-12):** AI Live Conversations, Homework Evaluator.
- **Phase 3 (Weeks 13+):** Full **hagwon LMS integration**.

### **CI/CD & Infrastructure**

✔ **Automated Testing & Deployment:** CI/CD pipelines.
✔ **Infrastructure as Code:** Terraform & Kubernetes.
✔ **Performance Monitoring:** Real-time tracking with observability tools.

[TODO] **More details to be added in [docs/deployment-strategy.md](docs/deployment-strategy.md).**

---

## 6. Security & Compliance

🔒 **Zero Trust Security Model** – Strict access controls & role-based permissions.  
📚 **PIPA Compliance** – Adhering to Korea’s data privacy regulations.  
✅ **AI Ethics & Governance** – Bias mitigation, explainability, & fairness.

[TODO] **More details to be added in [docs/security-governance.md](docs/security-governance.md).**

---

## 7. Enterprise Architecture & TOGAF Compliance

This project follows **TOGAF principles** for structured AI deployment.

### **📊 Architecture Diagram Levels**

1. **Conceptual** – High-level system overview for stakeholders.
2. **Logical** – AI components, workflows, and dependencies.
3. **Physical** – Deployment details (cloud resources, infrastructure).

📀 **TOGAF tracking in [docs/togaf-compliance.md](docs/togaf-compliance.md).**

---

## 8. Next Steps & Roadmap

✅ **Week 0 Submission:** Conceptual Architecture Diagram.  
💚 **Week 1:** Logical Diagram & System Flow.  
💚 **Week 2+:** Physical Diagram, Infrastructure, & Deployment.

📀 **Live tracking in [roadmap.md](../../roadmap.md).**

---

## 9. References & Further Reading

- **[Bootcamp Project Description](docs/project-requirements.md)**
- **[Enterprise Architecture Diagrams](diagrams/)**
- **Duolingo Language Report 2023** (Korean as 7th most learned language globally).
- **Korean Hagwon Market Statistics 2023** ($20B+ industry, 70,000 hagwons).
- **TOGAF & C4 Model** – Structured AI adoption methodologies.

---
