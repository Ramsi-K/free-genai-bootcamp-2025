# API Fundamentals

## 📌 Index

1. 🔹 [What is an API?](#what-is-an-api)
2. 🛠️ [Request/Response Structure](#requestresponse-structure)
3. 🔒 [API Security Best Practices](#api-security-best-practices)
4. 📄 [API Documentation](#api-documentation)

---

## **What is an API?**

An **Application Programming Interface (API)** allows different software systems to communicate with each other. APIs define rules and protocols for sending and receiving data.

### **Types of APIs:**

- **REST (Representational State Transfer)**

  - HTTP-based, uses JSON format
  - Stateless (each request is independent)
  - CRUD operations mapped to HTTP methods
    - `GET` - Retrieve data
    - `POST` - Create data
    - `PUT/PATCH` - Update data
    - `DELETE` - Remove data

- **gRPC (Google Remote Procedure Call)**
  - High-performance, binary format using Protocol Buffers
  - Uses HTTP/2 for multiplexed streams
  - More efficient than REST but requires defining service contracts

---

## **Request/Response Structure**

### **HTTP Methods & Usage:**

| Method   | Usage Example                         |
| -------- | ------------------------------------- |
| `GET`    | Retrieve user data (`GET /users/1`)   |
| `POST`   | Create a new resource (`POST /users`) |
| `PUT`    | Update a user (`PUT /users/1`)        |
| `DELETE` | Remove a resource (`DELETE /users/1`) |

### **HTTP Headers:**

- `Content-Type`: Specifies data format (e.g., `application/json`)
- `Authorization`: API key or token for authentication
- `Accept`: Defines expected response format

### **HTTP Status Codes:**

| Code | Meaning                        |
| ---- | ------------------------------ |
| 200  | OK (Success)                   |
| 201  | Created                        |
| 400  | Bad Request (Invalid Input)    |
| 401  | Unauthorized (Invalid API Key) |
| 403  | Forbidden (Access Denied)      |
| 404  | Not Found                      |
| 500  | Internal Server Error          |

---

## **API Security Best Practices**

### **1. Authentication & Authorization**

- Use **JWT (JSON Web Tokens)** for stateless authentication
- Implement **OAuth2** for third-party access control
- Require **API keys** or token-based authentication

### **2. Rate Limiting & Throttling**

- Prevent abuse by limiting requests per second (e.g., 100 requests/min)
- Use **HTTP 429 Too Many Requests** response code when limit is exceeded

### **3. Input Validation & Sanitization**

- Reject invalid or malformed requests
- Use libraries like `pydantic` (Python) for validation

### **4. HTTPS Encryption**

- Always use HTTPS to encrypt API traffic
- Protects against **Man-in-the-Middle (MitM) attacks**

---

## **API Documentation**

### **Swagger/OpenAPI Specification**

- Defines API endpoints, request/response structures, and authentication methods
- Generates interactive API documentation
- Example OpenAPI definition:

  ```yaml
  openapi: 3.0.0
  info:
    title: Example API
    version: 1.0.0
  paths:
    /users:
      get:
        summary: Get all users
        responses:
          '200':
            description: A list of users
  ```

### **Postman API Collections**

- Organize and test API requests
- Automate API testing

---

_Made by Ramsi K. – Part of the GenAI Bootcamp 2025 repository._
