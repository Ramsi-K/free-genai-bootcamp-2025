# Use the common base image (tag will be defined in docker-compose)
FROM listening-app-base:latest

# WORKDIR /app is inherited

# Install service-specific system dependencies (if any beyond base)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY services/transcript-processor/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy service-specific code
COPY services/transcript-processor/app.py ./app.py
COPY services/transcript-processor/guardrails.py ./guardrails.py

# Expose port for the service
EXPOSE 5000

# Command - Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
