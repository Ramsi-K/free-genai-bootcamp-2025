# ML104 - Architecting Generative AI Systems

*A lecture from the Machine Learning Mini Series by Rola Dali.  
The full series is available on YouTube: [Machine Learning Mini Series](https://youtube.com/playlist?list=PLBOxI5MJQLFs8-8vl_nTRte-gkNQeWsOa&si=3IaNr4OZUnaI9MNt).  
GitHub Repo: [miniMLseries](https://github.com/rdali/miniMLseries)*

## 📌 Table of Contents

- [1. Choosing the Right AI/ML Approach](#1-choosing-the-right-aiml-approach)
- [2. Trade-offs Between Predictive ML & Generative AI](#2-trade-offs-between-predictive-ml--generative-ai)
- [3. Cost Considerations in AI Architectures](#3-cost-considerations-in-ai-architectures)
- [4. Building Blocks of a GenAI System](#4-building-blocks-of-a-genai-system)
- [5. Enhancing GenAI System Performance](#5-enhancing-genai-system-performance)
- [6. Architecting a Scalable GenAI System](#6-architecting-a-scalable-genai-system)
- [7. Final Thoughts](#7-final-thoughts)

---

## 1. Choosing the Right AI/ML Approach

Before implementing an AI system, businesses should evaluate whether **AI/ML is the best tool for the problem**.  

### Rule-Based vs. AI-Based Automation  

- If the task is **deterministic** (follows clear rules), traditional **rule-based software or DevOps automation** may be more efficient.  
- If the task requires **cognition, reasoning, or complex pattern recognition**, **ML is a better choice**.

### Predictive ML vs. Generative AI  

| Feature         | Predictive ML | Generative AI (GenAI) |
|---------------|-------------|---------------------|
| **Use Cases**  | Classification, fraud detection, analytics | Text/image generation, summarization, translation |
| **Output**     | Fixed categories or numbers | Open-ended responses |
| **Customization** | Requires labeled datasets | Can work with unlabeled data |
| **Cost**       | Cheaper for specific tasks | Expensive training and inference |

---

## 2. Trade-offs Between Predictive ML & Generative AI

### When to Choose **Predictive ML**

- Tasks requiring **structured** and **deterministic** outputs.
- High compliance projects requiring **control and transparency**.
- Long-term cost savings when fine-tuning a custom model is feasible.

### When to Choose **Generative AI**

- When **speed to deployment** is critical, and a pre-trained foundation model can be used.
- When tasks require **open-ended** content creation (text, images, audio).
- When predictive ML does not have **pre-trained models available** for the task.

---

## 3. Cost Considerations in AI Architectures

AI system costs are typically broken down into:  

1. **Training Cost** – The computational expense of training a model.  
2. **Inference Cost** – The cost of running the model to generate predictions.  
3. **Total Cost of Ownership (TCO)** – Ongoing operational and maintenance expenses.  

### Cost Differences Between AI Models  

| Factor         | Predictive ML | Generative AI |
|--------------|-------------|-------------|
| **Model Size** | Smaller models | Large-scale foundation models |
| **Initial Cost** | High (custom training) | Lower (pre-trained models) |
| **Inference Cost** | Cheaper | More expensive (due to larger models) |
| **Control** | More customizable | Limited if using third-party models |

For example, **processing 1M pages** with AWS Textract (predictive ML) costs **$1,500/month**, whereas using a GenAI model (e.g., Claude, GPT) could cost **2x-10x more**.

---

## 4. Building Blocks of a GenAI System

A **basic GenAI system** consists of:  

1️⃣ **Model Call (Core AI Model)** – The foundational model (LLM, image generator, etc.).  
2️⃣ **Prompt Engineering** – Formatting input to optimize model output.  
3️⃣ **Knowledge Base (RAG)** – Integrating external sources for accurate responses.  
4️⃣ **Guardrails (Filters & Compliance)** – Ensuring safe and compliant AI outputs.  
5️⃣ **Model Gateway (Routing System)** – Directing requests to the best model based on task type.  
6️⃣ **Caching & Optimization** – Reducing model load to lower costs and improve response time.  

---

## 5. Enhancing GenAI System Performance

### 🔹 **Prompt Engineering**  

- Improve query structure to enhance output quality.  
- Add **context, instructions, or constraints** to shape responses.  
- Use **examples (zero-shot, one-shot, few-shot learning)** to guide model behavior.  

### 🔹 **Retrieval-Augmented Generation (RAG)**  

- Augment the AI model with **external knowledge bases**.  
- Helps **reduce hallucinations** and improve factual accuracy.  

### 🔹 **Guardrails (Input & Output Filtering)**  

- **Input Filters** – Ensuring user queries do not contain sensitive or unwanted data.  
- **Output Filters** – Ensuring AI responses do not contain harmful, biased, or misleading content.  

### 🔹 **Model Routing & Gateway**  

- Route AI requests to different models **based on task type** (e.g., coding, summarization, reasoning).  
- Enables **cost optimization** by using cheaper models for simpler tasks.  

### 🔹 **Caching & Latency Optimization**  

- Reduce costs by caching **frequent queries** to avoid repeated model calls.  
- Store embeddings and vectorized results for faster retrieval.

---

## 6. Architecting a Scalable GenAI System

### 🔹 **Modular System Design**

A well-architected system **abstracts** AI model calls so the backend can switch models seamlessly.

### 🔹 **Handling AI Model Calls Efficiently**

- Use **load balancing** to distribute queries across multiple instances.  
- Implement **rate limiting** to control API costs and prevent abuse.  

### 🔹 **Security & Compliance**

- Ensure **data privacy** when using third-party AI models (e.g., avoid exposing sensitive data).  
- Apply **role-based access controls (RBAC)** to AI-powered services.  

### 🔹 **Observability & Monitoring**

- Implement **logging & analytics** to track system performance and detect anomalies.  
- Use **feedback loops** to refine AI model behavior over time.  

---

## 7. Final Thoughts

### ✅ **Key Takeaways**

- **AI is a tool, not a solution by itself** – Choose ML/GenAI only if it fits the business need.  
- **Predictive ML is best for structured tasks**, while **GenAI is best for creative or open-ended tasks**.  
- **GenAI is expensive**, and cost-effective architectures should use **caching, model routing, and guardrails**.  
- **Security & compliance are critical** when integrating AI models, especially with third-party providers.  

---

## 🔗 Additional Resources

- 📖 *AI Engineering: Building AI Systems* – by Chip Huyen  
- 📖 *Designing Machine Learning Systems* – by Chip Huyen  
