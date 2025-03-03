#!/bin/bash

# Stop any existing containers
echo "Stopping any existing containers..."
docker compose down

# Remove any existing containers to avoid conflicts
echo "Removing any conflicting containers..."
docker rm -f ollama-server korean-vocab-importer 2>/dev/null || true

# Start the Ollama server only first
echo "Starting Ollama server..."
docker compose up -d ollama-server

# Wait for Ollama server to be healthy
echo "Waiting for Ollama server to be available..."
attempt=1
max_attempts=10
while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:11434/api/version > /dev/null; then
        echo "Ollama server is available!"
        break
    fi
    echo "Attempt $attempt of $max_attempts: Ollama server is not yet available. Waiting..."
    sleep 5
    attempt=$((attempt+1))
done

if [ $attempt -gt $max_attempts ]; then
    echo "Ollama server failed to become available after $max_attempts attempts."
    exit 1
fi

# Pull the smaller model (llama3.2:1b - around 800MB)
echo "Pulling the llama3.2:1b model..."
docker exec ollama-server ollama pull llama3.2:1b

# Check which models are available
echo "Available models:"
docker exec ollama-server ollama list

# Now start the vocabulary importer
echo "Starting vocabulary importer service..."
docker compose up -d korean-vocab-importer

# Wait for the vocab importer to start
echo "Waiting for vocabulary importer to start..."
attempt=1
max_attempts=10
while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "Vocabulary importer is available!"
        break
    fi
    echo "Attempt $attempt of $max_attempts: Vocabulary importer is not yet available. Waiting..."
    sleep 5
    attempt=$((attempt+1))
done

if [ $attempt -gt $max_attempts ]; then
    echo "Vocabulary importer failed to become available after $max_attempts attempts."
    echo "Checking logs:"
    docker logs korean-vocab-importer
    exit 1
fi

echo "Setup complete! You can now use the Korean Vocabulary Importer at http://localhost:8000"
echo ""
echo "Test with: curl -X POST http://localhost:8000/generate -H \"Content-Type: application/json\" -d '{\"theme\": \"Food\", \"count\": 5, \"include_example_sentences\": true}'"