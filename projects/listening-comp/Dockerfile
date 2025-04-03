# Use the common base image
FROM listening-app-base:latest  

# WORKDIR /app is inherited

# Copy root-level requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Verify numpy installation
RUN python -c "import numpy; print('Numpy version:', numpy.__version__)" || echo "Numpy not installed"

# Copy all service-specific files into the root structure
COPY services/transcript-processor/requirements.txt ./services/transcript-processor/
COPY services/audio-module/requirements.txt ./services/audio-module/
COPY services/question-module/requirements.txt ./services/question-module/

# Install service-specific dependencies
RUN pip install --no-cache-dir -r ./services/transcript-processor/requirements.txt
RUN pip install --no-cache-dir -r ./services/audio-module/requirements.txt
RUN pip install --no-cache-dir -r ./services/question-module/requirements.txt

# Copy all service-specific code
COPY services/transcript-processor/app.py ./services/transcript-processor/
COPY services/audio-module/app.py ./services/audio-module/
COPY services/question-module/app.py ./services/question-module/
COPY wrappers.py .

# Create necessary directories and __init__.py files
RUN mkdir -p services/metrics && \
    touch services/metrics/__init__.py && \
    mkdir -p /shared/data /shared/data/metrics

# Expose ports for all services
EXPOSE 5000 5001 5002 8000 8888

# Command to run the main service
CMD ["python", "mega_service.py"]
