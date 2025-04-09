# Korean Listening Comprehension App

This project is a terminal-based Korean Listening Comprehension application that helps users improve their listening and pronunciation skills through interactive quizzes based on YouTube video transcripts.

![Korean Listening Comprehension App](https://img.shields.io/badge/Language-Korean-blue)
![Platform](https://img.shields.io/badge/Platform-Terminal-lightgrey)

## Features

- **YouTube Integration**: Automatically fetches Korean transcripts from any YouTube video
- **Multiple Quiz Types**:
  - Basic fill-in-the-blank quizzes
  - TOPIK-style listening comprehension questions (using AI models)
- **AI-Powered Features**:
  - GPT-2 or EXAONE models for generating TOPIK-style questions
  - Korean-to-English translation for quiz sentences
- **Audio Controls**:
  - Text-to-speech with speed control (normal/slow)
  - Replay functionality during quizzes
- **Pronunciation Practice**:
  - Record and compare your pronunciation with reference audio
  - Get real-time similarity scores and feedback
- **Progress Tracking**:
  - Save and review your learning progress
  - Build a personal vocabulary bank from encountered words
- **Import/Export**:
  - Export quizzes to Anki flashcard format
  - Save and reload quiz sessions

## Requirements

To run this application, you need Python 3.8+ and the following dependencies:

- `numpy`: Mathematical operations for audio processing
- `librosa` & `soundfile`: Audio analysis and manipulation
- `PyAudio`: Recording audio for pronunciation practice
- `gTTS`: Text-to-speech functionality for Korean
- `pygame`: Audio playback
- `transformers` & `torch`: AI models for question generation
- `youtube_transcript_api`: Fetching YouTube transcripts
- `translate`: Basic translation functionality
- `pydub`: Additional audio processing
- `matplotlib`: Progress visualization

## Installation

### Using Conda (Recommended)

1. Clone the repository:

   ```bash
   git clone https://github.com/Ramsi-K/free-genai-bootcamp-2025.git
   ```

2. Navigate to the project directory:

   ```bash
   cd projects/listening-comp/listening-app-terminal
   ```

3. Create a Conda virtual environment:

   ```bash
   conda create -n korean-listening python=3.10
   ```

4. Activate the virtual environment:

   ```bash
   conda activate korean-listening
   ```

5. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

### Using pip

1. Clone the repository:

   ```bash
   git clone https://github.com/Ramsi-K/free-genai-bootcamp-2025.git
   ```

2. Navigate to the project directory:

   ```bash
   cd projects/listening-comp/listening-app-terminal
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running Locally (Recommended)

To run the application with full functionality (including audio recording and playback), execute the following command in your terminal:

```bash
python main.py
```

Follow the on-screen instructions to select a YouTube video and start the quiz.

### Docker Support (Limited Functionality)

> **⚠️ Important Note**: Docker containers have significant limitations with audio device access. Running the app in Docker will likely disable audio recording features (pronunciation practice) and may have issues with audio playback. For the full interactive experience, we strongly recommend running the app locally. There could also be issues with the Youtube api for fetching transcripts.

If you still want to use Docker for testing or development purposes:

1. Build the Docker image:

   ```bash
   docker build -t korean-listening-app .
   ```

2. Run the container:

   ```bash
   docker run -it --rm korean-listening-app
   ```

The Docker container includes all dependencies but may not provide the complete audio experience.

## Workflow

1. **Select Quiz Type**:

   - Basic Quiz (Fill-in-the-blank)
   - TOPIK-style Quiz (AI-generated listening comprehension)
   - Load a previously saved quiz

2. **Provide a YouTube URL**:

   - The application will fetch Korean transcripts from the video

3. **Choose Difficulty Level**:

   - Easy: Shorter sentences, slower audio playback
   - Medium: Standard difficulty
   - Hard: Longer sentences, more challenging questions

4. **Take the Quiz**:

   - Listen to the Korean audio
   - Select answers from multiple choice options
   - Use audio controls to replay at different speeds
   - Practice pronunciation of difficult sentences
   - View English translations on demand

5. **Review Results**:
   - See your final score
   - Track your progress over time
   - Build your vocabulary bank

## Key Features in Detail

### Pronunciation Practice

The pronunciation practice feature uses Dynamic Time Warping (DTW) to compare your spoken Korean with the reference pronunciation:

1. Listen to the correct pronunciation
2. Record your attempt
3. Receive a similarity score and feedback
4. Compare by listening to both recordings

### AI-Generated Questions

The application can use two different AI models:

- **GPT-2**: Faster, requires less resources
- **EXAONE**: More accurate Korean language understanding (when available)

### Vocabulary Building

Words from quizzes are automatically saved to your vocabulary bank, allowing you to:

- Browse your collected vocabulary
- View words in context
- Search for specific terms

## Project Structure

```text
korean-listening-comp/
├── app.py                  # Translation and AI question generation
├── audio_utils.py          # Audio playback and recording functions
├── config.py               # Application configuration
├── Dockerfile              # Docker configuration
├── main.py                 # Main application entry point
├── progress.py             # User progress tracking
├── requirements.txt        # Dependencies
└── vocabulary.py           # Vocabulary storage and management
```

## Acknowledgments

- [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api) for transcript retrieval
- [Transformers](https://github.com/huggingface/transformers) for AI model support
- [gTTS](https://github.com/pndurette/gTTS) for Korean text-to-speech functionality
