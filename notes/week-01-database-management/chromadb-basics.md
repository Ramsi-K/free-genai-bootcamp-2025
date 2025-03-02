# **ChromaDB Guide**

## 📌 Index

1. 🔹 [What is ChromaDB?](#1-what-is-chromadb)
2. 🛠️ [Setting Up ChromaDB](#2-setting-up-chromadb)
3. 📊 [Basic Operations in ChromaDB](#3-basic-operations-in-chromadb)
4. 🔗 [Integrating ChromaDB with AI Applications](#4-integrating-chromadb-with-ai-applications)

---

## **1. What is ChromaDB?**

### **Definition & Purpose**

- **ChromaDB** is an open-source, embedding-first vector database designed for AI-driven applications, especially **Retrieval-Augmented Generation (RAG)**.
- Unlike traditional databases, ChromaDB stores and queries **vector embeddings**, allowing efficient similarity searches.

### **Why Use ChromaDB?**

✅ **Optimized for AI/LLM workflows** (works well with LangChain, OpenAI, Hugging Face, etc.).
✅ **Python-first & developer-friendly** (simple API, easy to set up).
✅ **No external database server needed** (ideal for local development).
✅ **Supports metadata filtering** (store extra information alongside vectors).
✅ **Persistent and in-memory storage options** (flexible for production and testing).

---

## **2. Setting Up ChromaDB**

### **Installing ChromaDB**

```bash
pip install chromadb
```

### **Creating a ChromaDB Client**

- **Persistent Client** (Recommended for production):

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db") # Stores data in ./chroma_db
```

- **In-Memory Client** (For quick testing):

```python
client = chromadb.Client()
```

### **Creating a Collection**

```python
collection = client.create_collection(name="my_collection")
```

---

## **3. Basic Operations in ChromaDB**

### **Adding Data (Vector Embeddings)**

```python
collection.add(
    embeddings=[[1.1, 2.3, 3.2], [4.5, 6.9, 4.4]],
    documents=["This is a document", "This is another document"],
    metadatas=[{"source": "doc1"}, {"source": "doc2"}],
    ids=["id1", "id2"]
)
```

### **Performing a Similarity Search**

```python
results = collection.query(
    query_embeddings=[[1.2, 2.4, 3.1]],
    n_results=2
)
print(results)
```

### **Retrieving Data**

```python
retrieved_data = collection.get(ids=["id1", "id2"])
print(retrieved_data)
```

### **Filtering by Metadata**

```python
filtered_results = collection.query(
    query_embeddings=[[1.2, 2.4, 3.1]],
    n_results=2,
    where={"source": "doc1"}
)
print(filtered_results)
```

### **Updating Data**

```python
collection.update(
    ids=["id1"],
    metadatas=[{"source": "updated_doc1"}]
)
```

### **Deleting Data**

```python
collection.delete(ids=["id1"])
```

---

## **4. Integrating ChromaDB with AI Applications**

### **Using Different Embedding Functions**

- **Sentence Transformers:**

```python
from chromadb.utils import embedding_functions

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-mpnet-base-v2"
)
collection_with_ef = client.create_collection(name="collection_with_ef", embedding_function=sentence_transformer_ef)
```

- **OpenAI Embeddings:**

```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key"

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.environ["OPENAI_API_KEY"], model_name="text-embedding-ada-002"
)
collection_openai = client.create_collection(name="openai_collection", embedding_function=openai_ef)
```

### **ChromaDB in a Retrieval-Augmented Generation (RAG) System**

- **Retrieve relevant documents** using vector similarity.
- **Pass retrieved context** to an LLM for improved responses.

```python
query_embedding = openai_ef.embed(["Explain deep learning"])
retrieved_context = collection_openai.query(query_embeddings=query_embedding, n_results=3)

print(retrieved_context)
```

---

_Made by Ramsi K. – Part of the GenAI Bootcamp 2025 repository._
