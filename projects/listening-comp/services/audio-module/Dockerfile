FROM python:3.11-slim

WORKDIR /app

# Get OPEA components from GitHub
RUN apt-get update && \
    apt-get install -y git ffmpeg libsndfile1 && \
    git clone -b main https://github.com/opea-project/GenAIComps.git && \
    cp -r GenAIComps/comps . && \
    rm -rf GenAIComps && \
    apt-get remove -y git && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install requirements
COPY services/audio-module/requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Copy service files
COPY services/audio-module/app.py .
COPY wrappers.py .
COPY services/metrics/persistence.py ./services/metrics/

RUN mkdir -p /shared/data/audio /shared/data/metrics

ENV PYTHONPATH=/app

EXPOSE 5002

CMD ["python", "app.py"]