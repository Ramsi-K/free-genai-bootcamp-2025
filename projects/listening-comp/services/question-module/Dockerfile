# Build stage for comps
FROM python:3.11-slim AS comps-builder

WORKDIR /build

# Copy setup files
COPY setup.py /build/
COPY requirements.txt /build/

# Install build dependencies
RUN pip install --no-cache-dir build wheel setuptools

# Build comps wheel
RUN pip wheel --no-deps -w /wheels .

# Git stage
FROM python:3.11-slim AS git

RUN apt-get update && apt-get install -y --no-install-recommends git
RUN git clone --depth 1 https://github.com/opea-project/GenAIComps.git /GenAIComps

# Main stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy GenAIComps from git stage
COPY --from=git /GenAIComps/comps /app/GenAIComps/comps
COPY --from=git /GenAIComps/*.* /app/GenAIComps/
COPY --from=git /GenAIComps/LICENSE /app/GenAIComps/

# Install GenAIComps requirements
WORKDIR /app/GenAIComps
RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt
WORKDIR /app

# Set Python path to include GenAIComps
ENV PYTHONPATH=$PYTHONPATH:/app/GenAIComps

# Copy wheel from builder
COPY --from=comps-builder /wheels /wheels

# Copy and install service requirements
COPY services/question-module/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt /wheels/*.whl

# Copy service code
COPY services/question-module/ .

# Create directories
RUN mkdir -p /shared/data/chroma

ENV PYTHONPATH=/app

EXPOSE 5001

CMD ["python", "app.py"]