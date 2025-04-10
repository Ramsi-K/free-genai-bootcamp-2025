FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (build-essential for some Python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone LLaVA repositories
RUN git clone https://github.com/haotian-liu/LLaVA.git /llava && \
    cd /llava && \
    git clone https://github.com/mapluisch/LLaVA-CLI-with-multiple-images.git && \
    cp LLaVA-CLI-with-multiple-images/llava-multi-images.py .

# Install LLaVA dependencies
RUN cd /llava && \
    pip install --no-cache-dir -e .

# Copy our application
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Create required directories
RUN mkdir -p templates llava_output

# Move HTML template if needed
RUN if [ -f Hangul-calligraphy-practice.html ] && [ ! -f templates/Hangul-calligraphy-practice.html ]; then \
    cp Hangul-calligraphy-practice.html templates/; \
    fi

# Setup symlink for LLaVA-CLI script in our working directory
RUN ln -sf /llava/llava-multi-images.py .

# Expose the Flask port
EXPOSE 5000

CMD ["python", "server.py"]