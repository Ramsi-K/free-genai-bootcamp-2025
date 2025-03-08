FROM python:3.9-slim

WORKDIR /app

# Install system dependencies and dev tools for comps
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY services/transcript-processor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY services/transcript-processor/ .

# Create necessary directories
RUN mkdir -p /shared/data

# Set PYTHONPATH for OPEA imports
ENV PYTHONPATH=/app

EXPOSE 5000

CMD ["python", "app.py"]
