# Use the common base image
FROM listening-app-base:latest

# WORKDIR /app is inherited

# Install service-specific system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY services/question-module/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service-specific code
COPY services/question-module/app.py .
COPY wrappers.py .

# Create metrics directory structure
RUN mkdir -p services/metrics
COPY services/metrics/persistence.py ./services/metrics/
RUN touch services/metrics/__init__.py

# Create data directory
RUN mkdir -p /shared/data/chroma /shared/data/metrics

# Expose port
EXPOSE 5001

# Command
CMD ["python", "app.py"]
