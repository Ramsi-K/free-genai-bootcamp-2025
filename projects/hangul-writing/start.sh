#!/bin/bash

# Print banner
echo "=================================="
echo "Korean Handwriting Practice Startup"
echo "=================================="

# Check for Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

echo "🚀 Starting containers..."
docker-compose up -d

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama service to be ready..."
MAX_RETRIES=30
count=0
while [ $count -lt $MAX_RETRIES ]; do
    if curl -s --fail http://localhost:11434/api/tags &> /dev/null; then
        echo "✅ Ollama is ready!"
        break
    fi
    echo "Still waiting for Ollama to start... ($((count+1))/$MAX_RETRIES)"
    sleep 2
    count=$((count+1))
done

if [ $count -eq $MAX_RETRIES ]; then
    echo "❌ Ollama did not start properly. Check docker logs with 'docker-compose logs ollama'"
    exit 1
fi

# Pull the Korean model
echo "📥 Pulling Korean LLM model (this may take a while)..."
curl -X POST http://localhost:11434/api/pull -d '{"name": "kimjk/llama3.2-korean"}'

# Success message
echo ""
echo "✨ Setup complete! The app is running at http://localhost:5000"
echo "💡 Press Ctrl+C to stop watching logs"
echo "📝 Use 'docker-compose down' when you want to shut down the app"
echo ""

# Show logs
docker-compose logs -f web