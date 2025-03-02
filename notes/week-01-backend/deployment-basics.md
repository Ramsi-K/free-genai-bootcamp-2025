# **Backend Deployment Basics**

## 📌 Index

1. 🔹 [Environment Variables & Configuration Management](#environment-variables--configuration-management)
2. 🚀 [Running Flask with Gunicorn/Uvicorn](#running-flask-with-gunicornuvicorn)
3. 📊 [Logging & Error Handling in Production](#logging--error-handling-in-production)

---

## **1. Environment Variables & Configuration Management**

### **What are Environment Variables?**

- **Purpose**: Store sensitive data (e.g., API keys, database credentials) outside of the codebase.
- **Benefits**: Improves security and makes configuration easier across different environments (development, staging, production).

### **Using Environment Variables in Flask**

- **Install `python-dotenv`**:

  ```bash
  pip install python-dotenv
  ```

- **Create a `.env` File**:

  ```env
  SECRET_KEY=your_secret_key
  DATABASE_URI=sqlite:///app.db
  DEBUG=False
  ```

- **Load Environment Variables in Flask**:

  ```python
  from flask import Flask
  from dotenv import load_dotenv
  import os

  load_dotenv()
  app = Flask(__name__)
  app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
  app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
  ```

---

## **2. Running Flask with Gunicorn/Uvicorn**

### **Why Use Gunicorn/Uvicorn?**

- **Purpose**: WSGI/ASGI servers for running Flask apps in production.
- **Benefits**: Handles concurrent requests, improves performance, and ensures reliability.

### **Running Flask with Gunicorn**

- **Install Gunicorn**:

  ```bash
  pip install gunicorn
  ```

- **Run Flask App with Gunicorn**:

  ```bash
  gunicorn -w 4 app:app
  ```

  - `-w 4`: Use 4 worker processes.
  - `app:app`: `app` is the Flask application object.

### **Running Flask with Uvicorn**

- **Install Uvicorn**:

  ```bash
  pip install uvicorn
  ```

- **Run Flask App with Uvicorn**:

  ```bash
  uvicorn app:app --host 0.0.0.0 --port 8000
  ```

  - `--host 0.0.0.0`: Bind to all available IPs.
  - `--port 8000`: Run on port 8000.

---

## **3. Logging & Error Handling in Production**

### **Logging in Production**

- **Purpose**: Track application activity, errors, and performance.
- **Example Logging Setup**:

  ```python
  import logging
  from flask import Flask

  app = Flask(__name__)

  logging.basicConfig(filename='app.log', level=logging.ERROR)

  @app.route('/error')
  def error():
      try:
          raise ValueError("An error occurred")
      except ValueError as e:
          app.logger.error(f"Error: {e}")
          return "An error occurred", 500
  ```

### **Error Handling in Production**

- **Global Error Handlers**:

  ```python
  @app.errorhandler(404)
  def page_not_found(error):
      return "Page not found", 404

  @app.errorhandler(500)
  def internal_error(error):
      return "Internal server error", 500
  ```

### **Monitoring Tools**

- **Sentry**: Track errors and exceptions in real-time.
- **Prometheus + Grafana**: Monitor application performance and metrics.

---

_Made by Ramsi K. – Part of the GenAI Bootcamp 2025 repository._
