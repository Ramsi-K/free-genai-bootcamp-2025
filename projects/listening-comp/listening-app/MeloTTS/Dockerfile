# Use the base image
FROM listening-app-base:latest

# Copy the MeloTTS directory into the image
COPY . /app/MeloTTS

# Set the working directory
WORKDIR /app/MeloTTS

RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsndfile1 \
    espeak \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -e .


# Download the unidic dictionary
RUN python -m unidic download

# Run the init_downloads.py script to download the Korean model
RUN python melo/init_downloads.py

# Expose the port for the service
EXPOSE 8888

# Run the MeloTTS service
CMD ["python", "-m", "melo"]