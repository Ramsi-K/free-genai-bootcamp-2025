# **Vector Databases**

## 📌 Index

1. 🔹 [What is a Vector Database?](#1-what-is-a-vector-database)
2. 🛠️ [Comparing Vector Databases](#2-comparing-vector-databases)
3. 📊 [Use Cases in AI Applications](#3-use-cases-in-ai-applications)
4. 📝 [ChromaDB: A Python-First Vector Database](#4-chromadb-a-python-first-vector-database)

---

## **1. What is a Vector Database?**

### **Definition**

- **Purpose**: A database designed to store, index, and query vector embeddings.
- **Vector Embeddings**: Numerical representations of data (e.g., text, images) in high-dimensional space.

### **Why Use a Vector Database?**

✅ **Efficient Similarity Search**: Quickly find similar items based on vector distance (e.g., cosine similarity).  
✅ **AI/ML Integration**: Essential for applications like recommendation systems, semantic search, and natural language processing.  
✅ **Scalability**: Handles large-scale datasets with high-dimensional vectors.

---

## **2. Comparing Vector Databases**

### **Popular Vector Databases**

| Feature                | Pinecone | Weaviate  | pgvector  | Qdrant  | ChromaDB       |
| ---------------------- | -------- | --------- | --------- | ------- | -------------- |
| **Managed Service**    | ✅ Yes   | ❌ No     | ❌ No     | ❌ No   | ❌ No          |
| **Open Source**        | ❌ No    | ✅ Yes    | ✅ Yes    | ✅ Yes  | ✅ Yes         |
| **Hybrid Search**      | ❌ No    | ✅ Yes    | ❌ No     | ❌ No   | ✅ Yes         |
| **PostgreSQL Support** | ❌ No    | ❌ No     | ✅ Yes    | ❌ No   | ❌ No          |
| **Ease of Use**        | ✅ High  | ✅ Medium | ✅ Medium | ✅ High | ✅✅ Very High |

- **Pinecone**:
  - **Features**: Fully managed, scalable, and optimized for production.
  - **Use Cases**: Recommendation systems, semantic search.
- **Weaviate**:
  - **Features**: Open-source, supports hybrid search (vector + keyword).
  - **Use Cases**: Knowledge graphs, semantic search.
- **pgvector**:
  - **Features**: PostgreSQL extension for vector storage and search.
  - **Use Cases**: Applications already using PostgreSQL.
- **Qdrant**:
  - **Features**: Open-source, high-performance, and easy to use.
  - **Use Cases**: Semantic search, recommendation systems.
- **ChromaDB**:
  - **Features**: Python-first, developer-friendly, optimized for LLM-based applications.
  - **Use Cases**: Retrieval-Augmented Generation (RAG), AI-driven search, lightweight vector storage.

---

## **3. Use Cases in AI Applications**

### **Retrievers**

- **Purpose**: Retrieve relevant documents or data based on vector similarity.
- **Example**: Semantic search in a document database.

### **Embeddings**

- **Purpose**: Store embeddings generated by AI models (e.g., BERT, GPT).
- **Example**: Storing text embeddings for a chatbot to improve response accuracy.

### **Similarity Search**

- **Purpose**: Find similar items in a dataset (e.g., images, products).
- **Example**: Recommendation systems for e-commerce platforms.

### **Integration with AI Workflows**

- **Purpose**: Combine vector databases with AI pipelines for real-time inference and retrieval.
- **Example**: Using a vector database to store embeddings for a question-answering system.

---

## **4. ChromaDB: A Python-First Vector Database**

### **Why ChromaDB?**

✅ **Lightweight, Python-first, and easy to use**.  
✅ **Optimized for Retrieval-Augmented Generation (RAG) workflows**.  
✅ **Works seamlessly with OpenAI, LangChain, and other AI frameworks**.  
✅ **No need for an external database server**—ideal for local development.

### **Example: Using ChromaDB in Python**

```python
import chromadb

# Create a ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Create a new collection (like a table in SQL)
collection = chroma_client.get_or_create_collection("my_embeddings")

# Insert vector embeddings
collection.add(
    ids=["doc1", "doc2"],
    embeddings=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
    metadatas=[{"title": "First Document"}, {"title": "Second Document"}]
)

# Perform a similarity search
results = collection.query(query_embeddings=[[0.1, 0.2, 0.3]], n_results=1)
print(results)
```

---

_Made by Ramsi K. – Part of the GenAI Bootcamp 2025 repository._
