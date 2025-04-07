# Use the common base image
FROM listening-app-base:latest

# WORKDIR /app is inherited

# Install service-specific dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy service-specific code
COPY app.py ./app.py
COPY guardrails.py ./guardrails.py

# Expose port
EXPOSE 5000

# Command
CMD ["python", "app.py"]
