# Korean Vocabulary Importer

This project is part of the GenAI Bootcamp 2025, implementing a vocabulary generator and importer microservice using OPEA components and vLLM for local model serving.

## Project Overview

The Korean Vocabulary Importer is a web service that:

- Generates Korean vocabulary words for specific themes
- Exports vocabulary groups to JSON format
- Imports vocabulary from JSON files
- Integrates with OPEA's vLLM service for LLM-based vocabulary generation

This implementation follows the Level 200 "Vocab Importer" project requirements from the bootcamp curriculum:

- Creates an internal tool to generate vocabulary
- Exports generated vocabulary to JSON for later import
- Imports JSON files
- Uses an LLM (via OPEA's vLLM component)

## Architecture

This project demonstrates two possible architectural approaches:

### Microservice Architecture

In this approach, the vocabulary importer is deployed separately from the vLLM service, with each service having its own Docker container, build process, and lifecycle.

Benefits:

- Clear separation of concerns
- Independent versioning and deployment
- Follows the OPEA component architecture philosophy

### Megaservice Architecture (Implemented)

This project implements the "megaservice" approach, where multiple services are orchestrated together using a single Docker Compose file.

Benefits:

- Simpler deployment (one command starts everything)
- Services can easily communicate with each other
- Aligned with the bootcamp's goal to "construct your own Mega-service"

## Project Structure

```text
vocab-importer/
├── app.py                # FastAPI application
├── requirements.txt      # Python dependencies
├── Dockerfile            # Instructions to build the Docker image
└── docker-compose.yml    # Configuration for running services
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
  "name": "Food and Cuisine",
  "description": "Words related to Korean food and cuisine",
  "words": [
    {
      "hangul": "김치",
      "romanization": "gimchi",
      "english": ["kimchi"],
      "type": "noun"
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

## Usage

Once the services are running, you can interact with the API using these curl commands:

### Generate Korean vocabulary for a theme

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "Food and Cuisine",
    "count": 10,
    "include_example_sentences": true
  }'
```

### List all vocabulary groups

```bash
curl -X GET http://localhost:8000/groups
```

### Export a vocabulary group

```bash
curl -X GET http://localhost:8000/export/0 > korean_food_vocab.json
```

### Import a vocabulary group

```bash
curl -X POST http://localhost:8000/import \
  -H "Content-Type: application/json" \
  -d @korean_food_vocab.json
```

### Check service health

```bash
curl -X GET http://localhost:8000/health
```

## Technical Details

### Components

1. **vLLM Service**

   - Serves the LLM model (default: meta-llama/Llama-2-7b-chat-hf)
   - Provides an API compatible with OpenAI's completions API
   - Runs as a Docker container from the OPEA project

2. **Vocabulary Importer Service**
   - FastAPI application for generating and managing vocabulary
   - Connects to the vLLM service for LLM-based generation
   - Provides endpoints for generating, listing, exporting, and importing vocabulary

### Integration

The services are integrated through Docker networking, with the vocabulary importer service communicating with the vLLM service using HTTP requests.

### Environment Variables

The following environment variables can be used to configure the services:

- `REGISTRY`: Docker registry for vLLM image (default: opea)
- `TAG`: Docker image tag (default: latest)
- `LLM_ENDPOINT_PORT`: Port for the vLLM service (default: 8008)
- `DATA_PATH`: Path for data volumes (default: ./data)
- `LLM_MODEL_ID`: ID of the model to use (default: meta-llama/Llama-2-7b-chat-hf)

## Notes on OPEA Components

This project uses the Open Platform for Enterprise AI (OPEA) components, specifically the vLLM component for serving language models.

The vLLM component is containerized and provides an API for generating text completions, which we leverage for vocabulary generation.

For more information on OPEA components, see the [GenAIComps GitHub repository](https://github.com/opea-project/GenAIComps).

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
