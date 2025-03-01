# **Flask Backend Basics**

## 📌 Index

1. 🔹 [Setting Up a Flask API](#setting-up-a-flask-api)
2. 🛠️ [Handling Requests & Responses](#handling-requests--responses)
3. 🧩 [Flask Blueprints (Modularization)](#flask-blueprints-modularization)
4. 🔄 [Middleware (Logging, CORS)](#middleware-logging-cors)
5. 🧪 [Testing APIs with Postman/Thunder Client](#testing-apis-with-postmanthunder-client)

---

## **1. Setting Up a Flask API**

### **Project Structure**

```bash
my_flask_app/
├── app.py
├── routes/
│   └── api.py
├── models/
│   └── user.py
└── requirements.txt
```

- `app.py`: Entry point for the Flask application.
- `routes/`: Contains route definitions.
- `models/`: Defines database models.

### **Routing**

- **Basic Route:**

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask!"
```

- **Dynamic Routes:**

```python
@app.route('/user/<username>')
def show_user(username):
    return f"User: {username}"
```

---

## **2. Handling Requests & Responses**

### **HTTP Methods**

- **GET:** Retrieve data

```python
@app.route('/get-data', methods=['GET'])
def get_data():
    return {"message": "This is a GET request"}
```

- **POST:** Create a resource

```python
from flask import request

@app.route('/post-data', methods=['POST'])
def post_data():
    data = request.json
    return {"received_data": data}
```

- **PUT:** Update a resource

```python
@app.route('/update-data/<int:id>', methods=['PUT'])
def update_data(id):
    data = request.json
    return {"message": f"Updated record {id}", "data": data}
```

- **DELETE:** Remove a resource

```python
@app.route('/delete-data/<int:id>', methods=['DELETE'])
def delete_data(id):
    return {"message": f"Deleted record {id}"}
```

### **Request Object**

- `request.json`: For JSON data.
- `request.args`: For query parameters.
- `request.form`: For form data.

### **Response Object**

- **Returning JSON:**

```python
from flask import jsonify

@app.route('/json-response')
def json_response():
    return jsonify({"message": "This is a JSON response"})
```

---

## **3. Flask Blueprints (Modularization)**

### **What are Blueprints?**

- Organize routes into reusable components.
- Improves maintainability and scalability.

### **Example Blueprint**

- **Create a Blueprint:**

```python
from flask import Blueprint

api = Blueprint('api', __name__)

@api.route('/hello')
def hello():
    return "Hello from Blueprint!"
```

- **Register Blueprint:**

```python
from routes.api import api
app.register_blueprint(api, url_prefix='/api')
```

---

## **4. Middleware (Logging, CORS)**

### **Logging**

- Track application activity for debugging and monitoring.
- Example:

```python
import logging
from flask import Flask

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/log')
def log():
    logger.info("This is a log message")
    return "Logged a message"
```

### **CORS (Cross-Origin Resource Sharing)**

- Allow requests from different domains.
- **Install Flask-CORS:**

```bash
pip install flask-cors
```

- **Enable CORS:**

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
```

---

## **5. Testing APIs with Postman/Thunder Client**

### **Postman**

- Test API endpoints by sending requests and verifying responses.
- **Steps:**
  1. Create a new request in Postman.
  2. Set the HTTP method (GET, POST, etc.).
  3. Enter the API endpoint URL.
  4. Add headers or body data if needed.
  5. Send the request and check the response.

### **Thunder Client**

- Lightweight alternative to Postman for testing APIs.
- **Steps:**
  1. Install Thunder Client in VS Code.
  2. Create a new request.
  3. Enter the API endpoint and configure the request.
  4. Send the request and view the response.

---

_Made by Ramsi K. – Part of the GenAI Bootcamp 2025 repository._
