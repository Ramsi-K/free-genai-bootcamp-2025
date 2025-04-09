# Korean Listening Comprehension App

A web application that generates TOPIK-style listening comprehension questions from Korean YouTube videos.

## System Architecture

The application uses three Docker services:

1. `main` (Flask backend) - Handles video processing, question generation, and TTS
2. `frontend` (React) - User interface for submitting videos and practicing questions
3. `ollama` - Local LLM service for generating questions

## Prerequisites

- Docker and Docker Compose
- Internet connection for:
  - Downloading Docker images
  - Pulling Ollama model (~1.6GB)
  - Downloading TTS model on first run
  - Fetching YouTube transcripts

## Getting Started

### 1. Clone and Configure

```bash
# Clone the repository
git clone <repository-url>
cd <repository-directory>

# Create .env file with your settings
cp .env.example .env
```

### 2. Start Services

```bash
# Build and start all services
docker compose up -d

# Wait for services to initialize (1-2 minutes)
# The main service will download the TTS model on first run
```

### 3. Download Required Models

When first started, Ollama runs without any models. You must explicitly download the LLM model:

```bash
# Check which models are currently available
docker exec -it korean-ollama ollama list

# Download the required model (about 1.6GB)
docker exec -it korean-ollama ollama pull exaone3.5:2.4b
```

The model download happens in the background and might take several minutes depending on your connection. The app will work automatically once the model is ready - no restart needed.

### 4. Verify Setup

1. Check service health:

   ```bash
   docker compose ps
   ```

   All services should show as "running"

2. Access the application:

   ```
   http://localhost
   ```

3. Submit a Korean YouTube video URL to test the full pipeline

## Usage

1. Enter a YouTube URL containing Korean content with subtitles
2. Wait for processing:
   - Backend fetches transcript
   - LLM generates questions
   - TTS creates audio for questions
3. Practice with generated questions:
   - Listen to TTS audio
   - Choose answers
   - Get immediate feedback
   - Track your score

## Troubleshooting

### "Failed to generate questions from LLM"

This usually means either:

1. The Ollama model isn't downloaded yet

   ```bash
   # Check if model exists
   docker exec -it korean-ollama ollama list

   # Download if missing
   docker exec -it korean-ollama ollama pull exaone3.5:2.4b
   ```

2. The model is still downloading - check Ollama logs:
   ```bash
   docker compose logs -f ollama
   ```

### Model Download Taking Too Long

The required models are large:

- Ollama LLM (exaone3.5:2.4b): ~1.6GB
- TTS Model: ~1GB

On slower connections, initial setup might take 10-15 minutes. The application will work automatically once downloads complete.

### Other Issues

Check the logs:

```bash
# All services
docker compose logs

# Specific service
docker compose logs main
docker compose logs ollama
docker compose logs frontend
```

## Maintenance

### Cleanup

Remove all data (models, generated audio, database):

```bash
docker compose down -v
```

### Updates

Pull and rebuild:

```bash
git pull
docker compose build --no-cache
docker compose up -d
```

## License

This project is licensed under the Apache License 2.0.
