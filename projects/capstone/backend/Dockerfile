FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Setup directories and permissions
RUN mkdir -p /app/data && \
    chmod +x /app/scripts/start.sh

# Set environment variables
ENV PYTHONPATH=/app \
    SQLITE_DB_PATH=/app/data/hagxwon.db \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["/app/scripts/start.sh"]
