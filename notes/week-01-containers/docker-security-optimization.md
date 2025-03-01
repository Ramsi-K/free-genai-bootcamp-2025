# **Docker Security & Optimization**

## 📌 Index

1. 🔹 [Keeping Images Lightweight](#1-keeping-images-lightweight)
2. 🛠️ [Managing Environment Variables in Containers](#2-managing-environment-variables-in-containers)
3. 🔒 [Exposing Only Necessary Ports](#3-exposing-only-necessary-ports)

---

## **1. Keeping Images Lightweight**

### **Why Lightweight Images?**

- **Benefits**:
  - Faster builds and deployments.
  - Reduced attack surface (fewer vulnerabilities).
  - Lower storage and bandwidth usage.

### **Best Practices**

#### **Use Multi-Stage Builds**

```dockerfile
# Stage 1: Build
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
CMD ["python", "app.py"]
```

- **Why?**
  - Installs dependencies in a temporary build container and copies only essential files to the final image.
  - Keeps the runtime image smaller.

#### **Minimize Layers**

- Combine multiple `RUN` commands into one to reduce unnecessary layers.
- Example:

```dockerfile
RUN apt-get update && apt-get install -y \
    package1 \
    package2 \
    && rm -rf /var/lib/apt/lists/*
```

#### **Use Smaller Base Images**

- Prefer **alpine** or **slim** variants when available (e.g., `python:3.9-slim`).

---

## **2. Managing Environment Variables in Containers**

### **Why Manage Environment Variables?**

- Securely pass configuration and sensitive data (e.g., API keys, database credentials) to containers.

### **Methods**

#### **Using `docker run -e`**

```bash
docker run -e "DB_USER=admin" -e "DB_PASSWORD=secret" my-app
```

#### **Using `docker-compose.yml`**

```yaml
services:
  backend:
    image: my-app
    environment:
      - DB_USER=admin
      - DB_PASSWORD=secret
```

#### **Using `.env` Files**

- **Create a `.env` file:**

```env
DB_USER=admin
DB_PASSWORD=secret
```

- **Reference it in `docker-compose.yml`:**

```yaml
services:
  backend:
    image: my-app
    env_file:
      - .env
```

#### **Use Docker Secrets for Sensitive Data**

- Instead of environment variables, use **Docker Secrets** to store credentials securely.

```bash
echo "supersecret" | docker secret create db_password -
```

- Reference the secret in a service:

```yaml
services:
  backend:
    image: my-app
    secrets:
      - db_password
```

---

## **3. Exposing Only Necessary Ports**

### **Why Limit Exposed Ports?**

✅ **Security:** Reduces the attack surface by limiting access to only required ports.  
✅ **Performance:** Prevents unnecessary network traffic.

### **Best Practices**

#### **Expose Only Required Ports**

- **In `Dockerfile`:**

```dockerfile
EXPOSE 5000
```

- **In `docker-compose.yml`:**

```yaml
services:
  backend:
    image: my-app
    ports:
      - '5000:5000'
```

#### **Use Internal Networks**

- For inter-container communication, use Docker’s internal networking instead of exposing ports.

```yaml
services:
  backend:
    image: my-app
    networks:
      - internal_network
  db:
    image: postgres
    networks:
      - internal_network

networks:
  internal_network:
    driver: bridge
```

#### **Restrict External Access with Firewall Rules**

- **Use firewall rules** to allow only trusted IPs to access exposed ports.
- Example (Linux `iptables` rule to allow only specific IPs to access a port):

```bash
iptables -A INPUT -p tcp --dport 5000 -s 192.168.1.100 -j ACCEPT
iptables -A INPUT -p tcp --dport 5000 -j DROP
```

---

_Made by Ramsi K. – Part of the GenAI Bootcamp 2025 repository._
