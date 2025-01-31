# Tokenization in Large Language Models (LLMs)

## Introduction

Tokenization is a fundamental preprocessing step in natural language processing (NLP) where text is broken into smaller units called tokens. These tokens serve as the basic building blocks for Large Language Models (LLMs) like GPT, BERT, and T5.

Understanding tokenization methods is crucial for optimizing LLM performance, efficiency, and accuracy.

---

## What is Tokenization?

Tokenization converts raw text into discrete units that a model can process. These units can be:

- Words (Word-based tokenization)
- Subwords (Byte Pair Encoding, WordPiece, SentencePiece)
- Characters (Character-based tokenization)

``` mermaid
graph TD;
    A[Raw Text] -->|Tokenization| B[Tokens];
    B -->|Model Processes Tokens| C[LLM Input];
```

---

## Types of Tokenization

### (A) Word-Based Tokenization

- Splits text into words.
- Example: "I love machine learning." → `['I', 'love', 'machine', 'learning', '.']`
- Issues: Cannot handle out-of-vocabulary (OOV) words efficiently (e.g., new words or typos).

### (B) Subword Tokenization (Most Common in LLMs)

Subword tokenization is widely used in modern models to handle rare words more efficiently.

#### 1. Byte Pair Encoding (BPE)

- Merges frequent character sequences into subwords iteratively.
- Example: "unhappiness" → `['un', 'happiness']`

#### 2. WordPiece Tokenization (Used in BERT)

- Similar to BPE but uses likelihood-based merging.
- Example: "playing" → `['play', '##ing']`

#### 3. SentencePiece (Used in T5, ALBERT)

- Works directly on raw text, allowing it to handle languages without spaces (e.g., Chinese, Japanese).
- Example: "こんにちは" → `['こ', 'ん', 'に', 'ち', 'は']`

### (C) Character-Based Tokenization

- Each character is a token.
- Example: "Hello" → `['H', 'e', 'l', 'l', 'o']`
- Used in models like CharRNN but inefficient for large vocabularies.

---

## Vocabulary & Token Efficiency

Tokenization directly impacts context length and efficiency:

| Model | Tokenization Method | Average Tokens per Sentence |
|--------|----------------|--------------------------|
| GPT-4 | BPE | 8-10 |
| BERT | WordPiece | 9-12 |
| T5 | SentencePiece | 7-9 |

---

## How Tokenization Affects LLM Performance

Shorter token sequences → Faster processing
Fewer tokens → Lower cost in API-based models
Better OOV handling → Improved model accuracy

"three backticks" mermaid
graph LR;
    A[Efficient Tokenization] --> B[Fewer Tokens];
    B --> C[Reduced Model Cost];
    B --> D[Improved Accuracy];
"three backticks"

---
