# Use a suitable base image with Python and necessary build tools
# Using python:3.10-slim as an example, adjust if needed
FROM python:3.10-slim

# Install system dependencies required by libs like torch, soundfile, etc.
# Example: ffmpeg might be needed by TTS or audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    # Add other system dependencies if required by your Python packages
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file first to leverage Docker cache
COPY requirements.txt ./

# Install Python dependencies
# Consider using --no-cache-dir to reduce image size
# Ensure PyTorch index URL is handled correctly if needed
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (only main.py and potentially shared utils if any)
COPY main.py ./
# COPY any_utils.py ./ # If you have utility files used by main.py

# Create the directory for shared data within the container image
# The volume mount will overlay this at runtime
RUN mkdir -p /app/shared/data/audio

# Expose the port the app runs on
EXPOSE 8000

# Set the command to run the application
CMD ["python", "main.py"]
