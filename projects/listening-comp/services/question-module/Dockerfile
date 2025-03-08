# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

FROM python:3.9-slim

WORKDIR /app

# Install system dependencies and dev tools for comps
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY services/question-module/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY services/question-module/ .

# Create shared data directories
RUN mkdir -p /shared/data/chroma

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DATA_DIR=/shared/data
ENV CHROMA_DIR=/shared/data/chroma
ENV OLLAMA_HOST=http://ollama:11434
ENV LLM_MODEL=llama3:8b
ENV TEI_HOST=http://tei-embedding-service
ENV TEI_PORT=80
ENV PYTHONPATH=/app

EXPOSE 5001

CMD ["python", "app.py"]