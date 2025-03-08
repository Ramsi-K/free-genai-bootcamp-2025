# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY services/question-module/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY services/question-module/ .

# Create directories
RUN mkdir -p /shared/data/chroma

ENV PYTHONPATH=/app

EXPOSE 5001

CMD ["python", "app.py"]