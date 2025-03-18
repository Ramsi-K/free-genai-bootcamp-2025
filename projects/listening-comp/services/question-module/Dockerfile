FROM python:3.11-slim

WORKDIR /app/srcp/src

# Get OPEA components from GitHub
RUN apt-get update && \
    apt-get install -y git && \
    git clone -b main https://github.com/opea-project/GenAIComps.git && \
    cp -r GenAIComps/comps . && \
    rm -rf GenAIComps && \
    apt-get remove -y git && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install requirements
COPY services/question-module/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service files
COPY services/question-module/app.py .
COPY services/metrics/persistence.py ./services/metrics/
COPY wrappers.py .

RUN mkdir -p /shared/data/chroma /shared/data/metrics

ENV PYTHONPATH=/app

EXPOSE 5001

CMD ["python", "app.py"]