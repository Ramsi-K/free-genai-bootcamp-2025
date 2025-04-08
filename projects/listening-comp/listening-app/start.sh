#!/bin/bash

# Load environment variables, ignoring comments and empty lines
if [ -f .env ]; then
  export $(grep -vE '^#|^$' .env | xargs)
fi

# Function to check if a service is running
check_service() {
  local service_name=$1
  local port=$2
  echo "Checking if $service_name is running on port $port..."
  for i in {1..10}; do
    if nc -z localhost $port; then
      echo "$service_name is running."
      return 0
    fi
    echo "Waiting for $service_name to start..."
    sleep 2
  done
  echo "$service_name failed to start."
  exit 1
}

# Step 1: Initialize the database
python main.py init-db
if [ $? -ne 0 ]; then
  echo "Database initialization failed. Please check the logs for details."
  exit 1
fi

# Check if the database file exists
if [ ! -f "/shared/data/app.db" ]; then
  echo "Database file not found at /shared/data/app.db. Initialization may have failed."
  exit 1
fi

# Step 2: Start Ollama server and download the LLM model
if ! ollama list | grep -q "$LLM_MODEL"; then
  echo "Downloading LLM model: $LLM_MODEL"
  ollama pull "$LLM_MODEL"
else
  echo "LLM model $LLM_MODEL is already downloaded."
fi
ollama serve &
check_service "Ollama Server" 11434

# Step 3: Start all microservices
python services/transcript-processor/app.py &
check_service "Transcript Processor" 5000

python services/question-module/app.py &
check_service "Question Module" 5001

python services/audio-module/app.py &
check_service "Audio Module" 5002

# Step 4: Start the main application
python main.py &
check_service "Main Application" 8000

# Keep the script running
wait