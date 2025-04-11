# ASL Fingerspelling Detection Project

This project provides a web interface for practicing American Sign Language (ASL) fingerspelling. It uses a machine learning model to detect and recognize hand signs for the letters A-Z.

## Features

- Interactive practice mode to learn ASL fingerspelling
- Testing mode to check your skills against the model
- Video examples of each ASL letter
- Real-time feedback on your signing
- Progress tracking as you learn new letters

## Setup and Installation

### Quick Start with Docker Hub

For the easiest way to run this project:

```bash
# Pull the pre-built image
docker pull ramsik1/asl-fingerspelling:latest

# Run the container
docker run -p 5000:5000 ramsik1/asl-fingerspelling:latest
```

Then access the application at http://localhost:5000

> Note: Inference Model used may take a few minutes to load.

### Prerequisites

- Python 3.9+
- PyTorch
- Flask
- Webcam access

### Installation

1. Clone this repository:

```bash
git clone <repository-url>
cd ASL-fingerspelling/Detection
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python app.py
```

4. Open your browser and navigate to: http://localhost:5000

### Using Docker

Alternatively, you can run the application using Docker:

```bash
docker-compose up -d
```

## Usage

1. **Practice Mode**: Learn each ASL letter with video examples and practice with your webcam.

   - Click on letters in the grid to see detailed demonstrations
   - Use the "Start Camera" button to enable your webcam
   - Try forming the letter with your hand and click "Check My Sign" to test recognition

2. **Test Mode**: Test your knowledge of multiple letters in sequence.
   - A random letter will be shown as a target
   - Form the letter with your hand and click "Check My Sign"
   - The application will provide feedback on your signing

## Model Information

This project uses the [CLIP ASL Fingerspelling](https://huggingface.co/aalof/clipvision-asl-fingerspelling) model from Hugging Face, which has been trained on ASL fingerspelling images for high accuracy recognition.

ASL videos: [mirzamlk](https://www.shutterstock.com/g/mirzamlk/about)
