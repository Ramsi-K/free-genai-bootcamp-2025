FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY services/transcript-processor/requirements.txt .
COPY wrappers.py .
COPY services/metrics/persistence.py ./services/metrics/persistence.py

RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY services/transcript-processor/app.py .
COPY services/transcript-processor/guardrails.py .

# Create data directory
RUN mkdir -p /shared/data /shared/data/metrics

EXPOSE 5000

CMD ["python", "app.py"]
