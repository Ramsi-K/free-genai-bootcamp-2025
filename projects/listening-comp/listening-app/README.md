# Korean Listening Comprehension App - Implementation Guide

This guide provides comprehensive instructions on how to set up and deploy the Korean Listening Comprehension App.

## System Architecture

The application now consists of a simplified architecture with 3 main services managed by Docker Compose:

1.  **Main Backend (`main`)**: A single Flask service responsible for:
    - Extracting Korean transcripts from YouTube videos using `youtube_transcript_api`.
    - Communicating with the Ollama service to generate TOPIK-style listening comprehension questions based on the transcript.
    - Generating audio for the questions using a Hugging Face TTS model (`facebook/mms-tts-kor`).
    - Serving the API endpoints for the frontend.
    - Storing video data, transcripts, questions, and audio file references in a shared SQLite database.
2.  **Frontend (`frontend`)**: A React application providing the user interface for inputting URLs, viewing video details/transcripts, and taking the listening practice quizzes.
3.  **Ollama (`ollama`)**: Runs the large language model (e.g., Llama 3, Polyglot-Ko) used by the main backend service for question generation.

## Prerequisites

- Docker and Docker Compose
- Internet connection (for pulling images, models, and fetching transcripts)
- (Optional) NVIDIA GPU with CUDA support and NVIDIA Container Toolkit installed if you want Ollama to utilize the GPU for faster LLM inference.

## Getting Started

### 1. Clone the Repository

```bash
# Clone the repository (if you haven't already)
# git clone <repository_url>
cd <repository_directory>

# Create necessary shared data directories (Docker volumes handle this, but good practice)
mkdir -p shared/data/audio
```

_(The complex directory structure from the previous version is no longer needed)_

### 2. Set Up Environment Variables

Create a `.env` file in the root directory with the following content:

```dotenv
# Server host settings (usually fine as localhost for Docker)
HOST_IP=localhost

# API keys and tokens
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here # May be needed for TTS model download during build
YOUTUBE_API_KEY=your_youtube_api_key_here # Optional, but recommended for better video metadata

# Model settings
LLM_MODEL=llama3:8b # Or polyglot-ko:7b, etc. - Model used by Ollama
# OLLAMA_HOST=http://ollama:11434 # Defined in docker-compose.yaml

# GPU usage flag (primarily affects Ollama if configured in docker-compose.yaml)
USE_GPU=false

# Optional: Flask debug mode for main service
FLASK_DEBUG=false
```

- Replace `your_huggingface_token_here` if the TTS model requires authentication for download.
- Replace `your_youtube_api_key_here` with a YouTube Data API v3 key to fetch richer video metadata (title, author, etc.). If omitted, basic metadata will be used.
- Set `USE_GPU=true` if you have a compatible NVIDIA GPU and want Ollama to use it (you might need to uncomment the `deploy` section for the `ollama` service in `docker-compose.yaml`).

### 3. Build and Start the Services

Build and start all the services using Docker Compose:

```bash
docker-compose up --build -d
```

**Important:** The first startup might take some time.

- Docker needs to build the images, especially the `main` service which installs large Python libraries (PyTorch, Transformers).
- The `main` service will also download the Hugging Face TTS model (`facebook/mms-tts-kor`) on its first run. This can take several minutes depending on your internet connection. The service might be temporarily unresponsive or show errors in logs until the download completes.

### 4. Pull/Verify Ollama Model

Once the services are running (check with `docker-compose ps`), ensure the LLM model specified in your `.env` file (e.g., `exaone3.5:2.4b`) is available within the Ollama service.

```bash
# Check which models Ollama currently has
docker exec -it korean-ollama ollama list

# If your desired model (e.g., exaone3.5:2.4b) is not listed, pull it:
docker exec -it korean-ollama ollama pull exaone3.5:2.4b

# Or pull the default if you didn't change .env:
# docker exec -it korean-ollama ollama pull llama3:8b
```

_(Pulling the model can take time depending on its size and your connection.)_

### 5. Verify the Services are Running

After the Ollama model is confirmed/pulled, check that all services are running and healthy:

```bash
docker-compose ps
```

You should see `korean-main-backend`, `korean-frontend`, and `korean-ollama` running and ideally show a `healthy` status (it might take a minute after startup).

Test the health endpoints:

```bash
# Check main backend service (Flask)
curl http://localhost:8000/health

# Check Ollama service
curl http://localhost:11434/api/health
```

_(If the main service was unhealthy before the Ollama model was ready, you might need to restart it: `docker-compose restart korean-main-backend`)_

### 6. Access the Application

Once everything is running, access the application in your web browser:

```
http://localhost
```

_(Assumes the frontend service is mapped to port 80)_

## Usage Flow

1.  **Input a Korean YouTube URL**: On the home page, enter the URL of a YouTube video that has Korean subtitles available.
2.  **Process Video**: Click "Generate Questions". The backend will fetch the transcript, generate questions via Ollama, generate TTS audio, and save everything. You will be redirected to the Video Detail page.
3.  **View Details & Transcript**: On the Video Detail page, you can see video metadata, the full transcript, and segmented transcript parts.
4.  **Practice Listening**: If questions were successfully generated, click "Start Listening Practice" to go to the quiz page.
5.  **Take Quiz**: Listen to the audio for each question and select the best answer.

## Troubleshooting

### GPU Issues (for Ollama)

If you set `USE_GPU=true` and Ollama isn't using the GPU:

```bash
# Check if NVIDIA drivers are working on the host
nvidia-smi

# Verify NVIDIA Container Toolkit installation
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# Check Ollama container logs for GPU detection errors
docker-compose logs korean-ollama

# Ensure the deploy section in docker-compose.yaml for ollama is uncommented and correct
```

### Service Connection Issues

If the frontend can't reach the backend, or the backend can't reach Ollama:

```bash
# Check if containers are running and on the same network
docker-compose ps
docker network inspect listening-app_app_network # Network name might vary slightly

# Check backend logs for errors connecting to Ollama
docker-compose logs korean-main-backend

# Check frontend browser console for API call errors (F12)
```

### Model Download/Load Issues

If the main backend fails to load the TTS model:

```bash
# Check backend logs for download or loading errors
docker-compose logs korean-main-backend

# Ensure HUGGINGFACEHUB_API_TOKEN in .env is correct if needed
# Verify internet connectivity from the main container
docker exec -it korean-main-backend ping huggingface.co
```

If Ollama fails to load the LLM:

```bash
# Check Ollama logs
docker-compose logs korean-ollama

# Ensure the model was pulled correctly (Step 4)
```

### Transcript Issues

If you get errors about transcripts:

- Ensure the YouTube video has Korean subtitles available (auto-generated or manual).
- Check backend logs (`korean-main-backend`) for errors from `youtube_transcript_api`.

## Customization

### Using a Different LLM

1.  Update the `LLM_MODEL` variable in the `.env` file (e.g., `LLM_MODEL=llama3:latest`).
2.  Restart the services: `docker-compose up -d`
3.  Pull the new model into the running Ollama container:
    ```bash
    docker exec -it korean-ollama ollama pull <new_model_name:tag>
    ```

### Using a Different TTS Model

1.  Modify the `TTS_MODEL_NAME` variable directly within `main.py`.
2.  Rebuild the main service image: `docker-compose build main`
3.  Restart the services: `docker-compose up -d`
    _(Note: Ensure the chosen model is compatible with the `transformers` library's VitsModel/AutoTokenizer or adjust the TTS code in `main.py` accordingly)_

### CPU-Only Deployment

- Set `USE_GPU=false` in the `.env` file.
- Ensure the `deploy` section under the `ollama` service in `docker-compose.yaml` is commented out or removed.

## Maintenance

### Data Management

Data (SQLite DB, audio files, Ollama models) is stored in Docker volumes (`shared_data`, `ollama_data`). To clean up:

```bash
# List volumes
docker volume ls

# Remove specific volumes (caution: this deletes all generated data/models)
docker volume rm listening-app_shared_data
docker volume rm listening-app_ollama_data
```

_(Volume names might vary slightly based on the project directory name)_

### Updating the Application

To update the application code:

```bash
# Pull the latest code (if using Git)
# git pull

# Rebuild images and restart services
docker-compose down # Stop existing containers
docker-compose up --build -d # Rebuild and start
```

## Security Considerations

- The application is configured for local deployment. For production use, consider implementing proper authentication, input validation, rate limiting, and HTTPS.
- The Hugging Face token, if used, should have minimum required permissions.
- The YouTube API key, if used, should be restricted (e.g., by IP address or API referrer) in the Google Cloud Console.

## Contributing

Contributions are welcome! Please feel free to submit issues or Pull Requests.

## License

This project is licensed under the Apache License 2.0.
