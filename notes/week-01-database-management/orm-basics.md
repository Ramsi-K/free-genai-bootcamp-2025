# **ORMs (SQLAlchemy Basics)**

## 📌 Index

1. 🔹 [What is an ORM?](#1-what-is-an-orm)
2. 🏗️ [Using SQLAlchemy in Flask](#2-using-sqlalchemy-in-flask)
3. 🛠️ [CRUD Operations with SQLAlchemy](#3-crud-operations-with-sqlalchemy)
4. 📊 [Managing Migrations & Schema Changes](#4-managing-migrations--schema-changes)

---

## **1. What is an ORM?**

### **Definition & Purpose**

- **ORM (Object-Relational Mapping)** allows developers to interact with a database using **Python objects instead of raw SQL**.
- **Key Benefits:**
  ✅ Increases productivity by simplifying database interactions.
  ✅ Improves code readability with object-oriented queries.
  ✅ Provides database abstraction, making it easier to switch between databases.
  ✅ Prevents SQL injection vulnerabilities by handling queries safely.

### **Popular ORMs**

- **SQLAlchemy** (Python) – Powerful, flexible, and widely used in Flask.
- **Django ORM** (Python) – Built into Django, high-level abstraction.
- **Peewee** (Python) – Lightweight ORM for smaller projects.
- **GORM** (Go) – Developer-friendly ORM for Go.
- **Hibernate** (Java) – Popular ORM for Java applications.
- **TypeORM** (JavaScript) – ORM for Node.js and TypeScript.

---

## **2. Using SQLAlchemy in Flask**

### **Installation**

```bash
pip install flask-sqlalchemy
```

### **Basic Setup**

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)
```

### **Defining a Model**

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
```

### **Creating the Database & Tables**

```python
with app.app_context():
    db.create_all()
```

---

## **3. CRUD Operations with SQLAlchemy**

### **Create a New Record**

```python
new_user = User(username='john_doe', email='john@example.com')
db.session.add(new_user)
db.session.commit()
```

### **Read Records**

```python
user = User.query.filter_by(username='john_doe').first()
print(user.email)
```

### **Update a Record**

```python
user.email = 'john.doe@example.com'
db.session.commit()
```

### **Delete a Record**

```python
db.session.delete(user)
db.session.commit()
```

---

## **4. Managing Migrations & Schema Changes**

### **Why Use Migrations?**

- Tracks and applies changes to the database schema over time.
- Ensures consistency between the database schema and application models.

### **Using Alembic for Migrations**

#### **Install Alembic**

```bash
pip install alembic
```

#### **Initialize Alembic**

```bash
alembic init alembic
```

#### **Configure Alembic**

- Update `alembic.ini` and `env.py` to point to your database.

#### **Create a Migration**

```bash
alembic revision --autogenerate -m "Add new column"
```

#### **Apply the Migration**

```bash
alembic upgrade head
```

### **Example Migration: Adding a New Column**

#### **Update the Model**

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer)  # New column
```

#### **Generate and Apply Migration**

```bash
alembic revision --autogenerate -m "Add age column"
alembic upgrade head
```

---

This document covers **SQLAlchemy basics**, including model definitions, relationships, CRUD operations, and schema migrations. Next, we will explore **advanced SQLAlchemy features such as async support and performance optimization.**

```

```
