# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

FROM python:3.9-slim

WORKDIR /app

# Install system dependencies and dev tools for comps
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY services/audio-module/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY services/audio-module/ .

# Create necessary directories
RUN mkdir -p /shared/data/audio

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DATA_DIR=/shared/data
ENV AUDIO_DIR=/shared/data/audio
ENV PYTHONPATH=/app

EXPOSE 5002

CMD ["python", "app.py"]