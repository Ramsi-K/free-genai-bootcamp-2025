# Korean Handwriting Practice App ✍️🇰🇷

A GenAI-powered web application to improve your Korean handwriting by comparing your handwritten sentences with calligraphy examples using vision-language models.

## Features

- Generate Korean sentences based on input words using LLaMA 3.2-korean
- Display sentences in various Korean calligraphy fonts
- Capture handwriting via webcam
- Compare user handwriting with reference calligraphy using LLaVA
- Receive AI-generated feedback on accuracy, stroke style, spacing, and neatness

## Prerequisites

1. Python 3.8+ installed
2. Ollama installed with kimjk/llama3.2-korean model ([Ollama installation instructions](https://ollama.ai/))
3. LLaVA model setup (see below)

## Setup

### 1. Install Ollama and the Korean LLM model

Download and install Ollama from [ollama.ai](https://ollama.ai/), then run:

```bash
ollama pull kimjk/llama3.2-korean
```

### 2. Set up LLaVA

Follow the instructions from [mapluisch/LLaVA-CLI-with-multiple-images](https://github.com/mapluisch/LLaVA-CLI-with-multiple-images):

```bash
# Clone LLaVA repository and set it up according to their documentation
git clone https://github.com/haotian-liu/LLaVA.git
cd LLaVA
# Follow LLaVA setup instructions...

# Clone the LLaVA multi-image tool into the LLaVA directory
git clone https://github.com/mapluisch/LLaVA-CLI-with-multiple-images.git
cp LLaVA-CLI-with-multiple-images/llava-multi-images.py .
```

### 3. Install this project and its dependencies

```bash
# Clone this repository
git clone <your-repo-url>
cd <your-repo-directory>

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask server:

```bash
python server.py
```

2. Open your browser and navigate to:

```
http://localhost:5000
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

## License

[MIT License](LICENSE)
