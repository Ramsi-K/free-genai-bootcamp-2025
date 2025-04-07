# Use the common base image
FROM listening-app-base:latest

# Install service-specific dependencies
COPY services/audio-module/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service-specific code
COPY services/audio-module/app.py .

# Expose port
EXPOSE 5002

# Command
CMD ["python", "app.py"]
