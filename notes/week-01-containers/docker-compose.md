# **Docker Compose for Multi-Service Apps**

## 📌 Index

1. 🔹 [Setting Up a `docker-compose.yml`](#1-setting-up-a-docker-composeyml)
2. 🛠️ [Defining Services (Backend, Database, VectorDB)](#2-defining-services-backend-database-vectordb)
3. 🌐 [Networking Between Services](#3-networking-between-services)

---

## **1. Setting Up a `docker-compose.yml`**

### **What is Docker Compose?**

- **Docker Compose** is a tool for defining and running **multi-container applications**.
- It simplifies running multiple services (e.g., backend, database, vector store) in a **single configuration file**.

### **Basic `docker-compose.yml` Structure**

- Example:

```yaml
version: '3.8'
services:
  backend:
    image: my-flask-app
    build: .
    ports:
      - '5000:5000'
    environment:
      - FLASK_ENV=production
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## **2. Defining Services (Backend, Database, VectorDB)**

### **Backend Service**

- **Purpose**: Hosts the Flask application.
- **Configuration:**

```yaml
backend:
  image: my-flask-app
  build: .
  ports:
    - '5000:5000'
  environment:
    - FLASK_ENV=production
  depends_on:
    - db
```

### **Database Service**

- **Purpose**: Hosts the PostgreSQL database.
- **Configuration:**

```yaml
db:
  image: postgres:13
  environment:
    POSTGRES_USER: user
    POSTGRES_PASSWORD: password
    POSTGRES_DB: mydb
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

### **VectorDB Service**

- **Purpose**: Hosts a vector database like Qdrant or Weaviate.
- **Configuration:**

```yaml
vectordb:
  image: qdrant/qdrant
  ports:
    - '6333:6333'
  volumes:
    - qdrant_data:/qdrant/storage
```

---

## **3. Networking Between Services**

### **Service Discovery**

- Services can communicate **using their service names** instead of IP addresses.
- Example:
  - The **backend** connects to the **database** using `db:5432`.
  - The **backend** connects to the **vector database** using `vectordb:6333`.

### **Custom Networks**

- Define a custom network for **better security and isolation**.
- Example:

```yaml
networks:
  my_network:
    driver: bridge

services:
  backend:
    networks:
      - my_network
  db:
    networks:
      - my_network
  vectordb:
    networks:
      - my_network
```

### **Environment Variables for Networking**

- Example:

```yaml
backend:
  environment:
    DATABASE_URL: postgresql://user:password@db:5432/mydb
    VECTORDB_URL: http://vectordb:6333
```

---

_Made by Ramsi K. – Part of the GenAI Bootcamp 2025 repository._
