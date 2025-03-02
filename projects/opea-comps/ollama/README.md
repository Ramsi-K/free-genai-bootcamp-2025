<!---markdownlint-ignore MD024-->

# 🚀 Ollama Microservice

## **1️⃣ Overview**

As part of my microservices work for the bootcamp, I started by setting up **Ollama** as my first microservice. This document captures my experience, including the challenges I faced, the solutions I implemented, and key takeaways from the process.

## **2️⃣ Running Ollama with Docker Compose**

To start the Ollama container:

```bash
docker compose up -d
```

By default, **this does NOT download the model automatically**. You will need to download models manually **or modify the setup** (see below).

### **🔹 Setting Up a `.env` File**

Instead of hardcoding environment variables in `docker-compose.yml`, create a `.env` file in the same directory:

```ini
LLM_ENDPOINT_PORT=8008
LLM_MODEL_ID=llama3.2:1b
no_proxy=localhost,127.0.0.1
http_proxy=
https_proxy=
host_ip=192.168.1.100  # Replace with your machine's actual IP
```

Then modify `docker-compose.yml` to reference these values dynamically:

```yaml
services:
  ollama-server:
    image: ollama/ollama
    container_name: ollama-server
    ports:
      - '${LLM_ENDPOINT_PORT}:11434'
    environment:
      no_proxy: '${no_proxy}'
      http_proxy: '${http_proxy}'
      https_proxy: '${https_proxy}'
      LLM_MODEL_ID: '${LLM_MODEL_ID}'
      host_ip: '${host_ip}'

networks:
  default:
    driver: bridge
```

Now, when you run:

```bash
docker compose up -d
```

Docker will load environment variables from the `.env` file.

### **🔹 Finding Your IP Address**

To correctly set `host_ip`, run:

- **Windows (PowerShell):**

  ```powershell
  ipconfig | findstr /i "IPv4 Address"
  ```

- **Mac/Linux:**

  ```bash
  hostname -I | awk '{print $1}'
  ```

  Replace `host_ip` in `.env` with the IP shown in the output.. You will need to download models manually **or modify the setup** (see below).

## **3️⃣ Understanding the Ollama API Response Structure**

When calling Ollama’s API, the response structure contains additional metadata beyond just the generated text.

### **🔍 Key Fields in the Response**

| **Field**        | **Description**                                                  |
| ---------------- | ---------------------------------------------------------------- |
| `model`          | The model used for generation (e.g., `llama3.2:1b`)              |
| `response`       | The actual generated text content                                |
| `done`           | Indicates whether generation is complete (`true` means finished) |
| `done_reason`    | Why generation stopped (`"stop"`, `"length"`, etc.)              |
| `context`        | Internal state information used for further text generation      |
| `total_duration` | Total time taken for the request (in nanoseconds)                |

Example full response:

```json
{
  "model": "llama3.2:1b",
  "response": "The sky appears blue due to Rayleigh scattering, where shorter wavelengths of light are scattered more than longer wavelengths.",
  "done": true,
  "done_reason": "stop",
  "context": [128006,9125,128007,...],
  "total_duration": 5773023055
}
```

## **4️⃣ Common Issues & Fixes**

### **❌ Issue 1: "Model not found" Error**

#### **🔍 Why?**

The default Ollama Docker image **does not include models**, so you need to **download them manually**.

#### **✅ Solution: Manually Download the Model**

Run inside the container:

```bash
docker exec -it ollama-server ollama pull llama3
```

Then check if it's installed:

```bash
docker exec -it ollama-server ollama list
```

If it lists `llama3`, it's now available!

### **❌ Issue 2: Ollama Streams Token-by-Token Instead of Full Response**

#### **🔍 Why?**

By default, Ollama **streams responses token-by-token**, causing each word to appear as a separate JSON object.

#### **🔬 Example: Streaming Response (Default Behavior)**

```json
{"model":"llama3.2:1b","response":"The","done":false}
{"model":"llama3.2:1b","response":" sky","done":false}
{"model":"llama3.2:1b","response":" appears","done":false}
{"model":"llama3.2:1b","response":" blue","done":false}
...
{"model":"llama3.2:1b","response":"","done":true}
```

This happens because **each token is returned as a separate JSON object**.

#### **✅ Solution: Use `"stream": false` in Requests**

Modify the API request:

```bash
curl --noproxy "*" http://localhost:8008/api/generate -d '{
  "model": "llama3",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
```

#### **🔬 Example: Non-Streaming Response (`"stream": false`)**

```json
{
  "model": "llama3.2:1b",
  "response": "The sky appears blue due to Rayleigh scattering, where shorter wavelengths of light are scattered more than longer wavelengths.",
  "done": true
}
```

This forces a **single JSON response** instead of multiple tokenized parts.

#### **📝 When to Use Streaming vs. Non-Streaming?**

| **Mode**                         | **Best For**                                                                        |
| -------------------------------- | ----------------------------------------------------------------------------------- |
| ✅ `"stream": false` (Full JSON) | When you need the **entire response at once** (easier to process in scripts or UI). |
| ✅ `"stream": true` (Default)    | When you want a **real-time, token-by-token response** (ideal for chat UIs).        |

### **❌ Issue 3: Docker Compose Didn’t Download the Model Automatically**

#### **🔍 Why?**

The `docker-compose.yaml` only starts the Ollama **server**, but it does **not download models**.

#### \*\*✅ Solution: Download models by model ID

Visit the [Ollama Library](https://www.ollama.com/search), find the model you want to download and get the model ID for e.g. -

- LLama3.2 1b : 'llama3.2:1b
- Deepseek-r1 1.5b : 'deepseek-r1:1.5b'

When the container starts, run the following command to pull your chosen model

```bash
docker exec -it ollama-server ollama pull deepseek-r1:1.5b
```

### **5️⃣ Final Steps: Running & Testing Everything**

1️⃣ **Start the server**:

```bash
docker compose up -d
```

2️⃣ **Check if the model is installed**:

```bash
docker exec -it ollama-server ollama list
```

3️⃣ **Test the API (without streaming)**:

```bash
curl --noproxy "*" http://localhost:8008/api/generate -d '{
  "model": "llama3",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
```

4️⃣ **If model is missing, manually pull it**:

```bash
docker exec -it ollama-server ollama pull llama3
```

## **6️⃣ Results from Running Llama3.2:1b and DeepSeek**

### **Llama3.2:1b Response:**

```json
{
  "model": "llama3.2:1b",
  "response": "The sky appears blue to us because of a phenomenon called Rayleigh scattering, named after the British physicist Lord Rayleigh. He discovered that when sunlight enters Earth's atmosphere, it encounters tiny molecules of gases such as nitrogen and oxygen.

These gas molecules scatter the light in all directions, but they scatter shorter (blue) wavelengths more than longer (red) wavelengths. This is because the smaller molecules are more effective at scattering the blue light.

As a result, the blue light is dispersed throughout the atmosphere, giving the sky its blue color.",
  "done": true
}
```

### **DeepSeek-R1:1.5b Response:**

```json
{
  "model": "deepseek-r1:1.5b",
  "response": "The color of the sky, or its transparency, is due to a combination of factors, including atmospheric conditions, temperature, and the presence of water vapor in the air. When sunlight enters Earth's atmosphere, it travels through layers of gases and particles, known as the atmosphere. As sunlight interacts with these materials, some light is scattered away from us, while other wavelengths are absorbed or reflected.

At the top of Earth's atmosphere, most of the remaining sunlight appears blue because of the scattering effect caused by water vapor in the air. This phenomenon is a result of Rayleigh scattering and is why we experience a blue sky at sunrise or sunset.",
  "done": true
}
```

### **7️⃣ Stopping and Restarting Docker Compose**

- **If you just stopped the container:**

  ```bash
  docker compose start
  ```

  _(This will restart the previously stopped containers without recreating them.)_

- **If you removed the container with `docker compose down`, you must restart it completely:**

  ```bash
  docker compose up -d
  ```

  _(This will create fresh containers, but **models will be lost** if not manually pulled again.)_

⚠ **Warning:** If you run `docker compose down`, any downloaded models **will be lost**, and you will need to manually pull them again.
