# **Docker Basics for Backend Development**

## 📌 Index

1. 🔹 [Why Use Docker?](#1-why-use-docker))
2. 📦 [Writing a Dockerfile for Flask](#2-writing-a-dockerfile-for-flask)
3. 🚀 [Building & Running a Docker Container](#3-building--running-a-docker-container)
4. 🔍 [Debugging & Managing Containers](#4-debugging--managing-containers)

---

## **1. Why Use Docker?**

### **What is Docker?**

- **Docker** is a platform for packaging applications into **containers**.
- Containers bundle the application code along with dependencies to ensure consistency across different environments.

### **Benefits for Backend Development**

✅ **Consistency**: "Works on my machine" issues disappear since the environment is identical across dev, test, and production.  
✅ **Isolation**: Each container runs independently, preventing dependency conflicts.  
✅ **Portability**: Runs on any system that supports Docker (Windows, macOS, Linux, cloud servers).  
✅ **Efficiency**: Containers share OS resources, making them lightweight and fast.

---

## **2. Writing a Dockerfile for Flask**

### **Basic Dockerfile for Flask**

```dockerfile
# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### **Breaking Down the Dockerfile**

- `FROM python:3.9-slim` → Uses a minimal Python image for efficiency.
- `WORKDIR /app` → Sets the working directory in the container.
- `COPY requirements.txt .` → Copies only the dependencies file first (for efficient caching).
- `RUN pip install --no-cache-dir -r requirements.txt` → Installs dependencies.
- `COPY . .` → Copies the rest of the application files.
- `EXPOSE 5000` → Opens port **5000** for the Flask app.
- `CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]` → Runs the Flask app using **Gunicorn**.

---

## **3. Building & Running a Docker Container**

### **Building the Docker Image**

- Run this command in the project directory (where `Dockerfile` is located):

```bash
docker build -t flask-app .
```

- `-t flask-app` → Tags the image with a name (`flask-app`).
- `.` → Specifies the current directory as the build context.

### **Running the Docker Container**

- Start a container from the built image:

```bash
docker run -p 5000:5000 flask-app
```

- `-p 5000:5000` → Maps **port 5000** on the host to **port 5000** inside the container.
- `flask-app` → The name of the Docker image.

### **Running in Detached Mode**

- Run the container **in the background**:

```bash
docker run -d -p 5000:5000 flask-app
```

- `-d` → Detached mode (runs in the background).

---

## **4. Debugging & Managing Containers**

### **List Running Containers**

```bash
docker ps
```

- Shows **running** containers.

### **Stopping a Container**

```bash
docker stop <container_id>
```

- Replace `<container_id>` with the actual **container ID** from `docker ps`.

### **Viewing Container Logs**

```bash
docker logs <container_id>
```

- Useful for debugging errors inside the container.

### **Accessing a Running Container**

- Open an interactive shell inside the container:

```bash
docker exec -it <container_id> /bin/sh
```

- This allows you to manually inspect the container’s filesystem.

### **Removing Unused Containers & Images**

- Stop and remove all containers:

```bash
docker rm -f $(docker ps -aq)
```

- Remove all Docker images:

```bash
docker rmi -f $(docker images -aq)
```

---

_Made by Ramsi K. – Part of the GenAI Bootcamp 2025 repository._
