FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create shared data directory
RUN mkdir -p /shared/data/chroma

# Expose port
EXPOSE 5001

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DATA_DIR=/shared/data
ENV CHROMA_DIR=/shared/data/chroma
ENV OLLAMA_HOST=http://ollama:11434
ENV LLM_MODEL=llama3:8b
ENV TEI_HOST=http://tei-embedding-service
ENV TEI_PORT=80

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--timeout", "120", "app:app"]
