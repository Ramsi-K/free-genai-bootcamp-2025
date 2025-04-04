> **Note: This project was originally an attempt to integrate microservices using the GenAIComps (OPEA) orchestration framework. However, due to compatibility issues and lack of flexibility with custom services, this version has been deprecated. Please refer to the new implementation using plain Python orchestration in the main project directory.**

# Korean Listening Comprehension App - Implementation Guide

This guide provides comprehensive instructions on how to set up and deploy the Korean Listening Comprehension App, which is built using the OPEA framework.

## System Architecture

The application consists of 3 main microservices plus supporting services:

1. **Transcript Processor**: Extracts Korean content from YouTube videos and prepares the data
2. **Question Module**: Embeds text, generates TOPIK-style listening comprehension questions
3. **Audio Module**: Generates audio for questions using TTS
4. **Supporting Services**:
   - Ollama: Local LLM service for question generation
   - TEI Embedding: Vector embeddings for transcript segments
   - Frontend: React UI for user interaction

## Prerequisites

- Docker and Docker Compose
- NVIDIA GPU (recommended) with CUDA support
- NVIDIA Container Toolkit installed

## Getting Started

### 1. Clone the Repository and Set Up the Directory Structure

```bash
# Create project directory
mkdir -p korean-listening-app
cd korean-listening-app

# Create the folder structure
mkdir -p services/transcript-processor/utils
mkdir -p services/question-module/utils
mkdir -p services/audio-module/utils
mkdir -p frontend/public
mkdir -p frontend/src/components
mkdir -p frontend/src/pages
mkdir -p shared/models
mkdir -p shared/data
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory with the following content:

```bash
# Server host settings
HOST_IP=localhost

# API keys and tokens
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here

# Model settings
LLM_MODEL=llama3:8b
EMBEDDING_MODEL=jhgan/ko-sroberta-multitask
TTS_MODEL=PixelCat/melotts-korean-base

# GPU usage flag
USE_GPU=true
```

Replace `your_huggingface_token_here` with your actual HuggingFace API token, which is required for downloading models.

### 3. Copy the Files

Copy all the provided code files to their respective locations in the directory structure. Make sure to double-check the placement of each file.

### 4. Pull Required Models

Before starting the services, you'll need to pull the required models:

```bash
# Pull the Ollama model (llama3:8b)
docker run --rm -v ollama-data:/root/.ollama ollama/ollama pull llama3:8b

# Initialize directories with correct permissions
mkdir -p shared/data/audio
mkdir -p shared/data/chroma
chmod -R 777 shared
```

### 5. Build and Start the Services

Build and start all the services with Docker Compose:

```bash
docker-compose up -d
```

The first startup will take some time as Docker builds the images and downloads the necessary models.

### 6. Verify the Services are Running

Check that all the services are running properly:

```bash
docker-compose ps
```

Test each microservice's health endpoint:

```bash
curl http://localhost:5000/health
curl http://localhost:5001/health
curl http://localhost:5002/health
```

### 7. Access the Application

Once everything is running, you can access the application in your web browser:

```
http://localhost
```

## Usage Flow

1. **Input a Korean YouTube URL**: On the home page, enter a URL of a YouTube video with Korean content
2. **Generate Questions**: Navigate to the video details page and click "Generate Questions"
3. **Practice Listening**: Start the practice session and test your Korean listening comprehension skills

## Troubleshooting

### GPU Issues

If you encounter issues with GPU access:

```bash
# Check if NVIDIA drivers are working
nvidia-smi

# Verify NVIDIA Container Toolkit installation
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### Service Connection Issues

If services cannot communicate:

```bash
# Check if containers are on the same network
docker network inspect korean-listening-app_default

# Make sure ports are correctly exposed
docker-compose ps
```

### Model Download Issues

If models fail to download:

```bash
# Check HuggingFace token
docker logs korean-tei-embedding

# Verify internet connectivity from containers
docker exec -it korean-transcript-processor ping google.com
```

## Customization

### Using Different Models

To use different models, update the `.env` file:

```bash
# For a different LLM
LLM_MODEL=llama3:70b

# For a different embedding model
EMBEDDING_MODEL=your-preferred-model
```

### CPU-Only Deployment

If you don't have a GPU, update the `docker-compose.yaml` file by removing the `deploy` sections with GPU reservations, and set:

```bash
USE_GPU=false
```

## Maintenance

### Data Management

Data is stored in Docker volumes. To clean up:

```bash
# List volumes
docker volume ls

# Remove specific volumes (caution: this will delete all data)
docker volume rm korean-listening-app_shared-data
```

### Updating the Application

To update the application:

```bash
# Pull the latest code
git pull

# Rebuild and restart the services
docker-compose down
docker-compose build
docker-compose up -d
```

## Security Considerations

- The application is configured for local deployment. For production use, implement proper authentication and HTTPS.
- The Hugging Face token used has access to model downloads. Use a token with minimum required permissions.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0.
