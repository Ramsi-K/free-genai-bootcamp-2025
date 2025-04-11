#!/bin/bash

# Wait for Ollama to be ready
echo "Waiting for Ollama to be available..."
until $(curl --output /dev/null --silent --head --fail http://ollama:11434/api/health); do
    printf '.'
    sleep 5
done

echo "Ollama is available. Pulling the Ishara model..."
curl -X POST http://ollama:11434/api/pull -d '{"name": "ishara"}'
echo "Model pulled successfully. The application is ready to use."