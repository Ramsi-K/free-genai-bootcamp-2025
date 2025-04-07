# Use the base image
FROM listening-app-base:latest

# Set working directory
WORKDIR /app

# Copy only necessary files
COPY requirements.txt ./
COPY main.py ./
COPY services/ ./services/
COPY shared/ ./shared/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose necessary ports
EXPOSE 8000

# Set the entry point to main.py
CMD ["python", "main.py"]
