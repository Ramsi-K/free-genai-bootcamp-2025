# Korean Handwriting Practice App ✍️🇰🇷

A GenAI-powered web application to improve your Korean handwriting by comparing your handwritten sentences with calligraphy examples using vision-language models.

## Features

- Generate Korean sentences based on input words using LLaMA 3.2-korean
- Display sentences in various Korean calligraphy fonts
- Capture handwriting via webcam
- Compare user handwriting with reference calligraphy using LLaVA
- Receive AI-generated feedback on accuracy, stroke style, spacing, and neatness

## Setup Options

### Option 1: Docker Setup (Recommended)

The easiest way to run the application is with Docker, which automatically sets up both Ollama and LLaVA.

#### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/) and Docker Compose installed
- NVIDIA GPU with CUDA support (recommended)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) (for GPU acceleration)

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

#### Prerequisites

1. Python 3.8+ installed
2. Ollama installed ([Ollama installation instructions](https://ollama.ai/))
3. LLaVA setup (see below)

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

## License

[MIT License](LICENSE)
