# Korean Object Detection App (COCO-SSD)

This project is a real-time object detection web app that overlays Korean vocabulary labels on top of detected objects using the **COCO-SSD model (TensorFlow.js)**. It’s built for both AI experimentation and Korean language learning — with mobile-first optimization and Docker deployment.

---

## 🧠 Why This is Awesome

This isn’t just an object detector — it’s a **language learning tool**.

You point your camera at real objects — a cup, a dog, a book — and it teaches you the Korean word for each one in real time. Think of it like flashcards... but in your actual house.

Perfect for:

- Korean learners
- Tourists in Seoul
- Kids growing up abroad
- Anyone who hates memorizing vocab lists

---

## 📦 Project Structure

- `app/index.html` — main frontend file with canvas overlay + TensorFlow.js logic
- `Dockerfile` — builds a lightweight Nginx web server
- `docker-compose.yml` — launches the app and exposes it on port 8080

---

## 🚀 How to Run

### 1. Prerequisites

- Docker
- Docker Compose
- (Optional) [Ngrok](https://ngrok.com/) for mobile access via HTTPS

### 2. Build and Start

```bash
docker compose up --build
```

### 3. Open in Browser

- **Desktop:** http://localhost:8080
- **Phone (same Wi-Fi):**
  - Find your local IP with `ipconfig` or `ifconfig`
  - Visit `http://YOUR_IP:8080`

### 4. (Optional) Share with Ngrok

```bash
ngrok http 8080
```

Use the HTTPS URL on your phone — or generate a QR code for it [here](https://www.qr-code-generator.com/)

### 5. Stop the App

```bash
docker compose down
```

---

## 🌐 Tech Stack

- **COCO-SSD** — real-time object detection via TensorFlow.js
- **HTML Canvas** — draws bounding boxes and Korean labels
- **Docker + Nginx** — fast, easy deployment
- **Ngrok** — optional secure sharing over HTTPS

---

## 📱 Mobile Optimization

- Resolution capped at 640×480
- Inference runs every ~300ms
- Lightweight canvas redraw
- Runs well on iOS Safari (maybe a little slow)

---

## 🇰🇷 Korean Vocabulary Mapping

All 80 COCO-SSD object classes are labeled in Korean (with fallback to English). Example:

```json
{
  "dog": "강아지",
  "person": "사람",
  "book": "책",
  "cell phone": "휴대폰"
}
```

---

## ✨ Future Features

- TOPIK level filtering
- Audio pronunciation (TTS)
- Vocabulary challenges
- Voice-based guessing game
- “Kid Mode” with points & stickers

---

## 🛠 Maintainer

Made with frustration, triumph, and lots of 사랑 by Ramsi K.
