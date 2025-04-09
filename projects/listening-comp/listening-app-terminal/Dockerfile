FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for PyAudio and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    portaudio19-dev \
    python3-dev \
    ffmpeg \
    libsdl2-2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install all Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p data vocabulary recordings exports

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV SDL_AUDIODRIVER=dummy
ENV PYGAME_HIDE_SUPPORT_PROMPT=1

# Set the entry point
CMD ["python", "main.py"]