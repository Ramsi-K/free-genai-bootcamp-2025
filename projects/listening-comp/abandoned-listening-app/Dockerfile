# Simple Python base image
FROM python:3.10-slim

# Essential system packages only
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py ./
COPY components ./components/

# Create data directory
RUN mkdir -p /app/shared/data/audio

EXPOSE 8000

# Health check wrapper
COPY healthcheck.sh /
RUN chmod +x /healthcheck.sh

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["/healthcheck.sh"]

CMD ["python", "main.py"]
