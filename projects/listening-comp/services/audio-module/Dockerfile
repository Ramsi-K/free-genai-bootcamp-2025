# Use the common base image
FROM listening-app-base:latest

# Install service-specific dependencies
COPY services/audio-module/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -c "import numpy; print('Numpy version:', numpy.__version__)" || echo "Numpy not installed"

# Copy service-specific code
COPY wrappers.py .

# Expose port
EXPOSE 5002

# Command
CMD ["python", "app.py"]
