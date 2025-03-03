# Korean Vocabulary Importer

This project is part of the GenAI Bootcamp 2025, implementing a vocabulary generator and importer using Ollama for local model serving.

## Project Overview

The Korean Vocabulary Importer is a web application that:

- Generates Korean vocabulary words for specific themes using local LLMs
- Displays generated vocabulary in a user-friendly interface
- Saves vocabulary data to JSON files
- Leverages Ollama for efficient local model inference

This implementation follows the Level 200 "Vocab Importer" project requirements from the bootcamp curriculum:

- Creates an internal tool to generate vocabulary
- Exports generated vocabulary to JSON for later import
- Uses a local LLM serving the model via OPEA

## Architecture

The project uses a containerized approach with two main components:

1. **Ollama Server**: A lightweight inference server for running LLMs locally
2. **Flask Web Application**: A simple web service that communicates with Ollama and provides a user interface

Both components are orchestrated together using Docker Compose, making deployment straightforward.

## Project Structure

```text
vocab-importer/
├── app.py                # Flask application
├── static/               # Static files for the web UI
│   └── index.html        # Main web interface
├── data/                 # Directory for saved vocabulary files
├── requirements.txt      # Python dependencies
├── Dockerfile            # Instructions to build the Docker image
└── docker-compose.yaml   # Configuration for running services
```

## Korean Vocabulary Structure

The vocabulary follows this structure:

### Word Format

```json
{
  "hangul": "한국어",
  "romanization": "hangugeo",
  "type": "noun",
  "english": ["Korean language", "Korean"],
  "example_sentence": {
    "korean": "저는 한국어를 공부합니다.",
    "english": "I study Korean."
  }
}
```

### Group Format

```json
{
  "name": "Food",
  "description": "Words related to Food in Korean",
  "model_used": "llama3:latest",
  "words": [
    {
      "hangul": "김치",
      "romanization": "gimchi",
      "type": "noun",
      "english": ["kimchi", "fermented cabbage"],
      "example_sentence": {
        "korean": "한국 사람들은 매일 김치를 먹어요.",
        "english": "Korean people eat kimchi every day."
      }
    }
    // More words...
  ]
}
```

## Setup and Installation

1. Clone the repository
2. Navigate to the `vocab-importer` directory
3. Make sure Docker and Docker Compose are installed
4. Build and start the services:

```bash
docker-compose up -d
```

The application will be available at http://localhost:8000

## Using the Web Interface

1. Open your browser and go to http://localhost:8000
2. Select a model from the dropdown menu (the available models will be loaded from Ollama)
3. Enter a theme for vocabulary generation (e.g., "Food", "Travel", "Shopping")
4. Specify the number of words to generate
5. Click "Generate Vocabulary"
6. Once the vocabulary is generated, click "Save as JSON" to save it to the data folder

## API Endpoints

You can also interact with the API using curl commands:

### Check service health

```bash
curl http://localhost:8000/health
```

### List available models

```bash
curl http://localhost:8000/models
```

### Generate Korean vocabulary for a theme

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "Food",
    "count": 5,
    "model": "llama3:latest"
  }'
```

### List all vocabulary groups

```bash
curl http://localhost:8000/groups
```

### Export a vocabulary group

```bash
curl http://localhost:8000/export/0
```

### Import a vocabulary group

```bash
curl -X POST http://localhost:8000/import \
  -H "Content-Type: application/json" \
  -d @korean_food_vocab.json
```

### Save vocabulary to data folder

```bash
curl -X POST http://localhost:8000/save \
  -H "Content-Type: application/json" \
  -d @vocab_data.json
```

## Models

The application uses Ollama to serve local LLMs. Some models that work well with this application include:

- llama3:latest
- llama3.2:1b
- phi:latest

You can add more models to Ollama using the `ollama pull` command from the host machine. For details see [Ollama Implementation](../ollama/README.md)

## Example Korean Vocabulary Themes

Here are some example themes for Korean vocabulary:

1. Food and Cuisine
2. Shopping
3. Travel and Transportation
4. Family and Relationships
5. Time and Calendar
6. School and Education
7. Numbers and Counting
8. Colors and Appearance
9. Weather and Seasons
10. Sports and Activities

## Example Korean Vocabulary Groups

Here are some example themes for Korean vocabulary:

1. Food and Cuisine
2. Family and Relationships
3. Time and Calendar
4. Travel and Transportation
5. School and Education
6. Numbers and Counting
7. Colors and Appearance
8. Weather and Seasons
9. Health and Body Parts
10. Sports and Activities

## Resources for Korean Language Learning

- [Talk To Me In Korean](https://talktomeinkorean.com/)
- [How to Study Korean](https://www.howtostudykorean.com/)
- [Korean Grammar Dictionary](https://www.koreangrammatopics.com/)
- [TOPIK Guide](https://www.topikguide.com/)
