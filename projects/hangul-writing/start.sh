#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
  echo "No .env file found. Creating example file..."
  cp .env.example .env
  echo "Please edit .env file with your API keys and run this script again."
  exit 1
fi

# Check if required API keys are set
source .env

if [ -z "$IMGBB_API_KEY" ] || [ -z "$HF_API_KEY" ]; then
  echo "Error: Missing API keys in .env file"
  echo "Please set IMGBB_API_KEY and HF_API_KEY in your .env file"
  exit 1
fi

# Start the application with docker-compose
echo "Starting Hangul Calligraphy Practice app with API-based inference..."
docker-compose up