#!/bin/bash

# This script pulls the model before starting the services
set -e

# Define variables
MODEL_NAME=${LLM_MODEL_ID:-llama3.2:1b}
echo "Using model: $MODEL_NAME"

# Stop any existing containers
echo "Stopping any existing containers..."
docker compose down

# Start just the Ollama server
echo "Starting Ollama server..."
docker run -d --name ollama-temp -p 11434:11434 --pull always ollama/ollama:latest

# Wait for Ollama to be available
echo "Waiting for Ollama to be available..."
until curl -s http://localhost:11434/api/version > /dev/null; do
  echo "Waiting for Ollama server..."
  sleep 2
done
echo "Ollama is available."

# Pull the model
echo "Pulling model $MODEL_NAME..."
docker exec ollama-temp ollama pull $MODEL_NAME

# Show available models
echo "Available models:"
docker exec ollama-temp ollama list

# Stop and remove the temporary container
echo "Stopping temporary container..."
docker stop ollama-temp
docker rm ollama-temp

# Start all services
echo "Starting all services..."
docker compose up -d

echo "Setup complete! The Korean Vocabulary Importer should be available at http://localhost:8000"
echo ""
echo "Test with: curl -X POST http://localhost:8000/generate -H \"Content-Type: application/json\" -d '{\"theme\": \"Food\", \"count\": 5, \"include_example_sentences\": true}'"