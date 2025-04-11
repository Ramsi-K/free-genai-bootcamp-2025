FROM python:3.10-slim

# Install system dependencies (reduced since we don't need as many for API-based approach)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    wget \
    libgl1-mesa-glx \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies - no need for full torch CUDA since we're using API
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Create output directory for temporary files
RUN mkdir -p /app/llava_output

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_CACHE=/app/cache/transformers \
    HF_HOME=/app/cache/huggingface

# Copy application files
COPY . /app/

# Expose port
EXPOSE 5000

# Default command
CMD ["python", "server.py"]
