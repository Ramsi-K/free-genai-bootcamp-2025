# **SQL Basics (SQLite3 Focus)**

## 📌 Index

1. 🔹 [SQLite3 Overview](#1-sqlite3-overview)
2. 🛠️ [CRUD Operations in SQLite3](#2-crud-operations-in-sqlite3)
3. 📊 [Indexing & Query Optimization in SQLite3](#3-indexing--query-optimization-in-sqlite3)
4. 🔗 [Connecting SQLite3 to Flask](#4-connecting-sqlite3-to-flask))

---

## **1. SQLite3 Overview**

### **What is SQLite3?**

- **Purpose**: A lightweight, file-based SQL database engine.
- **Benefits**:
  - No server setup required.
  - Easy to use for development and testing.
  - Stores the entire database in a single file.

### **When to Use SQLite3?**

- **Use Cases**:
  - Small-scale applications.
  - Prototyping and development.
  - Embedded systems or mobile apps.
- **Limitations**:
  - Not suitable for high-concurrency or large-scale applications.

---

## **2. CRUD Operations in SQLite3**

### **CRUD Basics**

- **Create**: `INSERT INTO table_name (column1, column2) VALUES (value1, value2);`
- **Read**: `SELECT column1, column2 FROM table_name WHERE condition;`
- **Update**: `UPDATE table_name SET column1 = value1 WHERE condition;`
- **Delete**: `DELETE FROM table_name WHERE condition;`

### **Example Queries**

- **Create Table**:

  ```sql
  CREATE TABLE users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL
  );
  ```

- **Insert Data**:

  ```sql
  INSERT INTO users (name, email) VALUES ('John Doe', 'john@example.com');
  ```

- **Select Data**:

  ```sql
  SELECT * FROM users WHERE id = 1;
  ```

- **Update Data**:

  ```sql
  UPDATE users SET email = 'john.doe@example.com' WHERE id = 1;
  ```

- **Delete Data**:

  ```sql
  DELETE FROM users WHERE id = 1;
  ```

---

## **3. Indexing & Query Optimization in SQLite3**

### **Indexing**

- **Purpose**: Improves data retrieval speed by creating indexes on columns.
- **Example**:

  ```sql
  CREATE INDEX idx_name ON users (name);
  ```

- **When to Use Indexes**:
  - On columns frequently used in `WHERE`, `JOIN`, or `ORDER BY` clauses.
  - Avoid over-indexing, as it can slow down `INSERT` and `UPDATE` operations.

### **Query Optimization**

- **Avoid `SELECT *`**: Fetch only required columns.
- **Use `LIMIT`**: Limit the number of rows returned.
- **Optimize Joins**: Use indexed columns for joins.
- **Analyze Queries**: Use `EXPLAIN QUERY PLAN` to understand query performance.

  ```sql
  EXPLAIN QUERY PLAN SELECT * FROM users WHERE name = 'John Doe';
  ```

---

## **4. Connecting SQLite3 to Flask**

### **Using SQLite3 in Python**

- **Installation**: SQLite3 is included in Python’s standard library.
- **Basic Usage**:

  ```python
  import sqlite3

  # Connect to the database (or create it if it doesn't exist)
  conn = sqlite3.connect('example.db')
  cursor = conn.cursor()

  # Create a table
  cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)')

  # Insert data
  cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)', ('John Doe', 'john@example.com'))

  # Commit changes and close the connection
  conn.commit()
  conn.close()
  ```

### **Connecting SQLite3 to Flask**

- **Install Flask-SQLAlchemy**:

  ```bash
  pip install flask-sqlalchemy
  ```

- **Example**:

  ```python
  from flask import Flask
  from flask_sqlalchemy import SQLAlchemy

  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
  db = SQLAlchemy(app)

  class User(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.String(80), nullable=False)
      email = db.Column(db.String(120), unique=True, nullable=False)

  db.create_all()
  ```

---

_Made by Ramsi K. – Part of the GenAI Bootcamp 2025 repository._
