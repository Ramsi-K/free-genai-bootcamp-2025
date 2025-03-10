FROM python:3.11-slim AS git

# Install git and clone the GenAIComps repository
RUN apt-get update && apt-get install -y --no-install-recommends git
RUN git clone --depth 1 https://github.com/opea-project/GenAIComps.git /GenAIComps

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy GenAIComps files from the git stage
COPY --from=git /GenAIComps/comps /app/comps
COPY --from=git /GenAIComps/requirements.txt /app/comps_requirements.txt

# Install GenAIComps requirements
RUN pip install --no-cache-dir -r /app/comps_requirements.txt

# Copy service requirements and install
COPY services/transcript-processor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app.py directly
COPY services/transcript-processor/app.py .
COPY services/transcript-processor/guardrails.py .

# Create data directory
RUN mkdir -p /shared/data

# Set Python path to include comps
ENV PYTHONPATH=$PYTHONPATH:/app

# Enable Python output unbuffering for better logging
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "app.py"]
