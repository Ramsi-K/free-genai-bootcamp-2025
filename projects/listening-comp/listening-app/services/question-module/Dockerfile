# Use the common base image
FROM listening-app-base:latest

# WORKDIR /app is inherited

# Install service-specific dependencies
COPY services/question-module/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service-specific code
COPY services/question-module/app.py .

# Expose port
EXPOSE 5001

# Command
CMD ["python", "app.py"]
