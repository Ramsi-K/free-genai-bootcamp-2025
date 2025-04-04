# Use the common base image (tag will be defined in docker-compose)
FROM listening-app-base:latest

# WORKDIR /app is inherited

# Install service-specific system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY services/transcript-processor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service-specific code
COPY services/transcript-processor/app.py .
COPY services/transcript-processor/guardrails.py .
COPY wrappers.py .

# Create metrics directory structure
RUN mkdir -p services/metrics
COPY services/metrics/persistence.py ./services/metrics/
RUN touch services/metrics/__init__.py

# Create data directory (can also be done in base or via volume mount)
RUN mkdir -p /shared/data /shared/data/metrics

# Expose port
EXPOSE 5000

# Command
CMD ["python", "app.py"]
