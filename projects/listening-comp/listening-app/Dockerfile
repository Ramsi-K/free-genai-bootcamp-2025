# Use the base image
FROM listening-app-base:latest

# Set working directory
WORKDIR /app

# Copy only necessary files
COPY requirements.txt ./

# Install Python dependencies early to leverage Docker caching
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py ./
COPY services/ ./services/
COPY shared/ ./shared/

# Expose necessary ports
EXPOSE 8000

# Set the entry point to main.py
CMD ["python", "main.py"]
