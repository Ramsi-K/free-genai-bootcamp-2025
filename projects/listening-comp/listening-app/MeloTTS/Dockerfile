# Use Python 3.9 as the base image
FROM python:3.9-slim

# Install required dependencies
RUN apt-get update && apt-get install -y git && apt-get clean

# Clone the MeloTTS repository
RUN git clone https://github.com/myshell-ai/MeloTTS.git /app/MeloTTS

# Set the working directory
WORKDIR /app/MeloTTS

# Install MeloTTS dependencies
RUN pip install -e .

# Expose the port for the service
EXPOSE 8888

# Run the MeloTTS service
CMD ["python", "-m", "melo"]