# **ChromaDB Use Case: Combining Multiple Data Sources**

## 📌 Index

1. 🔹 [Overview: Structuring Data for Vector Search](#1-overview-structuring-data-for-vector-search)
2. 🏗️ [Defining Data Sources & Formats](#2-defining-data-sources--formats)
3. 🛠️ [Building a Multi-Source ChromaDB Collection](#3-building-a-multi-source-chromadb-collection)
4. 🔍 [Querying, Filtering & Retrieving Data](#4-querying-filtering--retrieving-data)

---

## **1. Overview: Structuring Data for Vector Search**

### **Why Use ChromaDB for Multi-Source Data?**

- Stores **different types of educational content** (words, grammar, books, YouTube captions, LLM-generated material).
- Enables **semantic search** across different formats (text, structured data, transcripts).
- Supports **metadata filtering** to refine search results based on category (e.g., "beginner words" or "grammar rules").

---

## **2. Defining Data Sources & Formats**

### **Dataset Breakdown**

| Data                            | Source                | Type                                  | Example                     | Metadata                     |
| ------------------------------- | --------------------- | ------------------------------------- | --------------------------- | ---------------------------- |
| **Common Words List**           | Dictionary-style text | "apple: A fruit, often red or green." | Difficulty Level, Frequency |
| **Full Word Frequency List**    | Structured text       | "Word: 'run'                          | Frequency: 5000"            | Usage Rank, Grammar Category |
| **Books/Stories**               | Paragraph text        | "Once upon a time..."                 | Author, Difficulty Level    |
| **LLM-Generated Teaching Data** | AI Text               | "Lesson: How to use past tense"       | AI Model, Source            |
| **YouTube Captions**            | Transcript            | "[00:02:15] The weather today..."     | Video URL, Topic            |

---

## **3. Building a Multi-Source ChromaDB Collection**

### **Installation & Setup**

```bash
pip install chromadb
```

### **Creating a Persistent ChromaDB Client**

```python
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./chroma_db")

# Initialize an embedding function
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")

collection = client.get_or_create_collection(name="language_learning", embedding_function=embedding_function)
```

### **Ingesting Multiple Data Types**

```python
data = [
    {"text": "apple", "meaning": "a fruit", "example": "I ate an apple.", "type": "word"},
    {"text": "run", "meaning": "to move quickly", "example": "He runs every morning.", "type": "word"},
    {"text": "Present Simple", "explanation": "Used for habits and general truths.", "type": "grammar"},
    {"text": "Once upon a time...", "source": "Storybook 1", "type": "book"},
    {"text": "In this lesson, we will learn about verbs.", "source": "LLM Lesson 1", "type": "lesson"},
    {"text": "Welcome to today's video on pronunciation.", "source": "YouTube Video 1", "type": "video"},
]

embeddings = []
metadatas = []
ids = []

for idx, item in enumerate(data):
    embeddings.append(embedding_function(item["text"]))
    metadatas.append({"type": item["type"], "source": item.get("source", "")})
    ids.append(f"id{idx}")

collection.add(
    embeddings=embeddings,
    metadatas=metadatas,
    ids=ids
)
```

---

## **4. Querying, Filtering & Retrieving Data**

### **Performing a Semantic Similarity Search**

```python
query = "How do I use the present simple tense?"
query_embedding = embedding_function(query)

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5  # Retrieve top 5 results
)

for result in results["metadatas"][0]:
    print(f"Type: {result['type']}, Source: {result.get('source', 'N/A')}")
```

### **Filtering by Metadata**

```python
filtered_results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5,
    where={"type": {"$in": ["grammar", "lesson"]}}  # Filter to specific content types
)

for result in filtered_results["metadatas"][0]:
    print(f"Type: {result['type']}, Source: {result.get('source', 'N/A')}")
```

### **Example Output**

```bash
Type: grammar, Source: N/A
Type: lesson, Source: LLM Lesson 1
Type: word, Source: N/A
Type: book, Source: Storybook 1
Type: video, Source: YouTube Video 1
```

---

_Made by Ramsi K. – Part of the GenAI Bootcamp 2025 repository._
