# ML103 - Introduction to Generative AI

*A lecture from the Machine Learning Mini Series by Rola Dali.  
The full series is available on YouTube: [Machine Learning Mini Series](https://youtube.com/playlist?list=PLBOxI5MJQLFs8-8vl_nTRte-gkNQeWsOa&si=3IaNr4OZUnaI9MNt).  
GitHub Repo: [miniMLseries](https://github.com/rdali/miniMLseries)*


## 📌 Table of Contents

- [1. What is Generative AI?](#1️⃣-what-is-generative-ai)
- [2. Large Language Models (LLMs)](#2️⃣-large-language-models-llms)
- [3. Challenges & Limitations of LLMs](#3️⃣-challenges--limitations-of-llms)
- [4. Key AI & LLM Terminology](#4️⃣-key-ai--llm-terminology)
- [5. Evolution & Scale of LLMs](#5️⃣-evolution--scale-of-llms)
- [6. Generative AI vs. Predictive ML](#6️⃣-generative-ai-vs-predictive-ml)
- [7. Enhancing LLM Performance](#7️⃣-enhancing-llm-performance)
- [8. Tokenization & Word Representations](#8️⃣-tokenization--word-representations)
- [9. Transformer Architecture](#9️⃣-transformer-architecture)
- [10. The Future of Generative AI](#-the-future-of-generative-ai)

---

## 1️⃣ What is Generative AI?

Generative AI (**GenAI**) is a subset of **machine learning (ML)** that creates **new** content, such as text, images, audio, or video.  
Unlike traditional ML models that classify or predict within predefined constraints, **GenAI produces novel outputs** based on learned data.

### 🔹 Key Milestone

GenAI became widely known after **OpenAI released ChatGPT (Nov 2022)**, making advanced AI accessible to the public.

### 🔹 GenAI Modalities

- **Text** → Large Language Models (LLMs) (e.g., GPT-4, Claude, Bard)
- **Images** → AI-generated art (e.g., Midjourney, Stable Diffusion, DALL·E)
- **Audio** → AI music/speech synthesis (e.g., ElevenLabs, AudioCraft)
- **Video** → AI video generation (e.g., Sora by OpenAI, Runway)

---

## 2️⃣ Large Language Models (LLMs)

LLMs are **deep-learning models** designed to **process and generate human-like text**. They function as **next-word predictors**, estimating the probability of the next token in a sequence.

### 🔹 Key Features

- Trained on massive datasets including books, websites, and code.
- Understands syntax (word structure) and semantics (meaning).
- Performs a wide range of NLP tasks such as summarization, translation, and Q&A.
- Uses self-supervised learning, removing the need for labeled training data.

### 🔹 LLM Use Cases

- 📝 **Text Generation** → AI writers, news summarization (e.g., Jasper AI, Copy.ai)
- 💬 **Chatbots & Conversational AI** → Customer support, AI assistants (e.g., ChatGPT, Bard)
- 🌍 **Machine Translation** → Google Translate, DeepL
- 🤖 **Code Assistance** → GitHub Copilot, ChatGPT Code Interpreter
- 🔍 **Search & Retrieval** → AI-enhanced search engines (e.g., Google Search with BERT)

---

## 3️⃣ Challenges & Limitations of LLMs

❌ **Hallucinations** → LLMs may generate **plausible but incorrect information**.  
❌ **Knowledge Cutoffs** → Models only "know" data up to their last training update.  
❌ **Bias & Toxicity** → Reflects biases present in training data.  
❌ **Context Window Limits** → LLMs process a **fixed number of tokens at a time**.  
❌ **Weak at Math & Structured Data** → Struggles with calculations, tables, and logic.

---

## 4️⃣ Key AI & LLM Terminology

- **Transformer** → The neural network architecture behind LLMs (*"Attention Is All You Need"*, 2017).  
- **Token** → A unit of input/output (word, subword, or character).  
- **Embedding** → A numerical vector representation of text for AI processing.  
- **Retrieval-Augmented Generation (RAG)** → Uses external knowledge sources to improve accuracy.  
- **Foundational Model** → A large, general-purpose AI model trained on vast datasets.  

---

## 5️⃣ Evolution & Scale of LLMs

- **LLM sizes have grown exponentially** (e.g., BERT **340M** → GPT-4 **1.8T** parameters).  
- Training requires **huge compute power** (e.g., **16,000+ NVIDIA H100 GPUs, costing $65M–$85M** per model).  
- AI efficiency improvements focus on **reducing compute costs & memory requirements**.

---

## 6️⃣ Generative AI vs. Predictive ML

| Feature            | Predictive ML         | Generative AI (LLMs)  |
|-------------------|---------------------|----------------------|
| **Training Data**  | Uses labeled data   | Uses massive unlabeled datasets |
| **Output**        | Fixed categories/numbers | Open-ended responses |
| **Use Cases**     | Fraud detection, classification | Chatbots, text/image generation |
| **Cost**         | Lower training & inference cost | Expensive training but reusable models |
| **Customization** | Often trained per use case | General-purpose but can be fine-tuned |

---

## 7️⃣ Enhancing LLM Performance

### 🔹 Weight-Preserving Techniques (No Model Retraining)

- **Prompt Engineering** – Optimizing input prompts for better responses.
- **Retrieval-Augmented Generation (RAG)** – Incorporating external knowledge bases.
- **Fine-Tuning & Adaptation** – Adjusting model responses with minimal data.

### 🔹 Weight-Altering Techniques (Modifying the Model Itself)

- **Parameter-Efficient Fine-Tuning (PEFT)** – Efficient small-scale tuning.
- **Quantization** – Reducing model size for faster inference.

---

## 8️⃣ Tokenization & Word Representations

- **Tokenization:** Splits text into smaller pieces (*tokens*), affecting how LLMs process data.  
- **Embedding:** Converts text into mathematical representations (vectors).  
  - Early methods: **Bag of Words, TF-IDF**  
  - **Breakthrough (2013):** *Word2Vec* enabled AI to **"understand" word relationships (e.g., King - Man + Woman = Queen).**  
  - **Transformers (2017):** Enabled **deep contextual understanding** of text.  

---

## 9️⃣ Transformer Architecture

The **transformer** is the neural network architecture that powers **LLMs**.

### 🔹 Key Components

- **Self-Attention Mechanism** → Assigns importance to words in a sentence.  
- **Multi-Head Attention** → Tracks multiple contextual relationships.  
- **Positional Encoding** → Retains word order in parallel processing.  

### 🔹 Why Transformers Replaced RNNs

✔️ **Parallelization** → Faster training & inference.  
✔️ **Better handling of long-range dependencies** in text.  

---

## 🔟 The Future of Generative AI

- **LLMs will continue scaling**, with model sizes increasing by roughly 10x per year.
- **Optimization & efficiency improvements** will drive more sustainable AI training.
- **Greater AI accessibility**, with more open-source models becoming available.
- **Emergence of new architectures** beyond transformers for faster, more efficient AI.

---

## Summary

✔️ **Generative AI enables machines to generate new, human-like content.**  
✔️ **LLMs are transformer-based AI models used in chatbots, coding, translation, and more.**  
✔️ **LLMs have limitations (hallucinations, bias, high compute costs).**  
✔️ **Techniques like RAG, fine-tuning, and prompt engineering improve LLM performance.**  
✔️ **The future of AI will focus on scalability, optimization, and accessibility.**  

---
*Made by Ramsi K. – Part of the GenAI Bootcamp 2025 repository.*
