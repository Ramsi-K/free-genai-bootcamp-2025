# Hangul Writing Project

This project is part of the Gen AI Bootcamp 2025 and focuses on creating an application for learning and practicing Hangul writing. The project leverages modern AI techniques to provide an interactive and engaging experience for users.

## Features

- Interactive Hangul writing practice.
- AI-based feedback on writing accuracy.
- User-friendly interface for learners of all levels.
- Generate Korean sentences based on input words using LLaMA 3.2-korean
- Display sentences in various Korean calligraphy fonts
- Capture handwriting via webcam
- Compare user handwriting with reference calligraphy using LLaVA
- Receive AI-generated feedback on accuracy, stroke style, spacing, and neatness

## Prerequisites

- Docker
- Docker Compose
- NVIDIA GPU with CUDA support (recommended)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) (for GPU acceleration)
- Python 3.8+ installed
- Ollama installed ([Ollama installation instructions](https://ollama.ai/))
- LLaVA setup (see below)

## Getting Started

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd hangul-writing
   ```
3. Build and start the application using Docker Compose:
   ```bash
   docker-compose up --build
   ```
4. Access the application at `http://localhost:8000`.

## Setup Options

### Option 1: Docker Setup (Recommended)

The easiest way to run the application is with Docker, which automatically sets up both Ollama and LLaVA.

#### Steps

1. Build and start the containers:

```bash
docker-compose up --build
```

2. Once the containers are running, pull the Korean LLM model:

```bash
curl -X POST http://localhost:11434/api/pull -d '{"name": "kimjk/llama3.2-korean"}'
```

3. Open your browser and navigate to:

```
http://localhost:5000
```

### Option 2: Manual Setup

If you prefer to set up components manually:

#### Steps

1. **Install Ollama and the Korean LLM model**:

   ```bash
   # Install Ollama from ollama.ai
   ollama pull kimjk/llama3.2-korean
   ```

2. **Set up LLaVA**:

   ```bash
   # Clone LLaVA repository
   git clone https://github.com/haotian-liu/LLaVA.git
   cd LLaVA

   # Install LLaVA dependencies (consider using a virtual environment)
   pip install -e .

   # Add the multi-image tool
   git clone https://github.com/mapluisch/LLaVA-CLI-with-multiple-images.git
   cp LLaVA-CLI-with-multiple-images/llava-multi-images.py .
   ```

3. **Install this project and its dependencies**:

   ```bash
   # Clone this repository
   git clone <your-repo-url>
   cd <your-repo-directory>

   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Create symlink to LLaVA script** (replace path with your actual LLaVA directory):

   ```bash
   ln -s /path/to/LLaVA/llava-multi-images.py .
   ```

5. **Start the Flask server**:

   ```bash
   python server.py
   ```

## Project Structure

- `docker-compose.yaml`: Configuration for Docker Compose to set up the application.
- `Dockerfile`: Instructions to build the Docker image.
- `README.md`: Project documentation.

## Usage

1. **Enter a Korean Word**: Type a Korean word in the input field and click "Generate Practice"
2. **View Generated Sentence**: A simple sentence using your word will be displayed
3. **Select Font Style**: Choose a Korean calligraphy font to display the reference text
4. **Practice Writing**: Copy the sentence on paper, trying to match the calligraphy style
5. **Capture Your Writing**: Click "Open Webcam to Capture" and take a photo of your handwritten sentence
6. **Receive Feedback**: The AI will compare your handwriting to the reference and provide feedback

## System Architecture

- **Frontend**: HTML + JavaScript for user interface
- **Server**: Flask server to handle API requests
- **Sentence Generation**: Uses `generate_sentence.py` with LLaMA 3.2 Korean via Ollama
- **Handwriting Comparison**: Uses `compare_with_llava.py` to invoke LLaVA with the reference and user images
- **Image Processing**: Uses LLaVA-CLI-with-multiple-images for concatenating and analyzing images

## Troubleshooting

### Ollama Issues

- If using Docker and Ollama is unreachable, make sure the container is running: `docker-compose ps`
- Check Ollama logs: `docker-compose logs ollama`

### LLaVA Issues

- Ensure the model downloads correctly - check the logs for any errors
- If using manual setup, verify your paths are correct and the symlink points to the LLaVA script
- Make sure you have sufficient GPU memory for the LLaVA model

### Web App Issues

- Check Flask server logs for any errors
- For webcam issues, ensure your browser has permission to access the webcam

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.
