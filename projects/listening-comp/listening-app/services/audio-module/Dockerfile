# Use the common base image
FROM listening-app-base:latest

# Install service-specific dependencies
COPY audio-module/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set the working directory
WORKDIR /app

# Copy service-specific code
COPY audio-module/app.py .
COPY ../metrics /app/services/metrics

# Expose port
EXPOSE 5002

# Command
CMD ["python", "app.py"]
