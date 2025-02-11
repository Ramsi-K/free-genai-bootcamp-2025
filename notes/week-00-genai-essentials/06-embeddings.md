# Embeddings in Large Language Models (LLMs)

## Introduction

Embeddings are numerical representations of words, phrases, or entire documents in a high-dimensional space. They allow **Large Language Models (LLMs)** to capture semantic meaning and relationships between words, enabling more efficient and context-aware processing of text.

---

## What are Embeddings?

Embeddings transform words or sentences into dense vector representations. Instead of treating words as separate entities, embeddings capture **contextual relationships, similarities, and meaning**.

``` mermaid
graph TD;
    A[Raw Text] -->|Tokenization| B[Tokens];
    B -->|Embedding Layer| C[Vector Representations];
    C -->|Input to Neural Network| D[LLM Processing];
```

### Example: Word Embedding Space

- **Similar words have similar vector representations.**
- **Example:**
  - `vector("king") - vector("man") + vector("woman") ≈ vector("queen")`

---

## Types of Embeddings

### 1. Word Embeddings

Word embeddings assign **fixed-size vectors to words** based on their semantic meaning.

#### Popular Word Embedding Models

- **Word2Vec** (Google) – Learns relationships between words using Skip-gram & CBOW.
- **GloVe** (Stanford) – Generates embeddings based on word co-occurrence matrices.
- **FastText** (Facebook) – Extends Word2Vec with subword information for better handling of rare words.

### 2. Sentence Embeddings

Sentence embeddings encode entire **sentences or paragraphs** into a single vector, preserving their contextual meaning.

#### **Popular Sentence Embedding Models:**

- **BERT Embeddings** – Captures deep bidirectional context.
- **Sentence-BERT (SBERT)** – Optimized for similarity comparisons.
- **Universal Sentence Encoder (USE)** – Designed for general NLP applications.

### 3. Contextualized Embeddings

Contextualized embeddings capture **word meaning based on sentence context**, unlike traditional word embeddings which assign the same vector regardless of context.

#### **Examples:**

- "The bank of the river was peaceful."
- "He deposited money in the bank."
- **LLMs assign different vector representations to 'bank' in each case.**

---

## Measuring Similarity Between Embeddings

### Cosine Similarity

To compare embeddings, **cosine similarity** is used. It measures how similar two vectors are in a multi-dimensional space.

``` mermaid
graph LR;
    A[Vector A] -->|Angle θ| B[Vector B];
    A -->|Cosine Similarity| C[Similarity Score];
```

### Cosine Similarity Formula

$$
    \cos(\theta) = \frac{A \cdot B}{\|A\| \|B\|}
$$

**Example Use Cases:**

- Finding **similar documents** in search engines.
- Detecting **plagiarism and duplicate content**.
- Matching **user queries to relevant FAQs** in chatbots.

---

## Applications of Embeddings

- **Semantic Search** – Improves search engines by ranking results based on meaning rather than keywords.  
- **Recommendation Systems** – Suggests content by comparing user preferences with similar items.  
- **Machine Translation** – Captures relationships between words in different languages for accurate translation.  
- **Text Classification & Sentiment Analysis** – Helps categorize and analyze large-scale text datasets.  

---

## Conclusion

Embeddings are a fundamental component of modern NLP and LLMs, enabling efficient text representation and semantic understanding. Next, we explore **Vector Databases**, which store and retrieve embeddings efficiently for AI-driven applications.

---
*Made by Ramsi K. – Part of the GenAI Bootcamp 2025 repository.*
