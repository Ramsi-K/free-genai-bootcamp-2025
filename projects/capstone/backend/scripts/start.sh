#!/bin/bash
set -e

echo "Setting up environment..."
mkdir -p /app/data

echo "Checking database..."
if [ ! -f "$SQLITE_DB_PATH" ]; then
    echo "Running database migrations..."
    python scripts/manage_migrations.py upgrade head
fi

echo "Starting FastAPI server..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --no-access-log
