# Korean Language Learning Chatbot

A multi-agent chatbot system built with CrewAI that helps users learn Korean language through interactive personas (AhjummaGPT and AhjussiGPT) with Retrieval-Augmented Generation (RAG) capabilities.

## Features

- **Multiple Agent Personas**: Interact with different Korean personalities
  - **AhjummaGPT**: A direct, no-nonsense Korean auntie who provides honest and spicy responses
  - **AhjussiGPT**: A wise Korean uncle who shares proverbs and cultural context
- **RAG Capabilities**: Uses Qdrant vector database to provide relevant language examples
- **GPU-Accelerated**: Leverages GPU for embeddings and LLM processing via Ollama
- **Dockerized**: Easy deployment with containerized services

## Architecture

The system consists of three main components:

1. **Multi-Agent Framework**: Built with CrewAI to orchestrate different agents
2. **Vector Database**: Qdrant for storing and retrieving text chunks with metadata
3. **Local LLM**: Ollama for generating responses through personas

## Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- GPU (optional, but recommended)

### Installation

1. Clone the repository:

```bash
git https://github.com/Ramsi-K/free-genai-bootcamp-2025
cd projects/multi-agent-chatbot
```

2. Start the Docker containers:

```bash
docker-compose up -d
```

3. To check if everything is running correctly, you can:

```bash
docker logs -f korean-chatbot
```

Manual Loading:

1. Pull the LLM model:

```bash
docker exec -it korean-ollama ollama pull kimjk/llama3.2-korean
```

2. Process text files and create chunks:

```bash
python process_text_data.py
```

3. Populate the vector database:

```bash
python populate_qdrant.py
```

## Usage

### Start the chatbot

```bash
python main.py
```

### Example interactions

```text
You: 안녕하세요! Can you teach me how to use the verb 먹다?

AhjummaGPT: Ya! You want to learn 먹다? That means "to eat"! Why you
don't know such basic word? *adjusts glasses*

First, conjugation:
- 먹어요 (I eat/You eat) - polite present
- 먹었어요 (I ate/You ate) - polite past
- 먹을 거예요 (I will eat) - future

Example: 나는 김치를 먹어요 (I eat kimchi)

Now practice! Say what you ate yesterday! Don't be lazy!
```

## Data Processing Pipeline

1. **Text Processing**: Chunks text files with metadata
2. **Vector Embedding**: Converts text to vectors using sentence-transformers
3. **Storage**: Indexes in Qdrant for semantic search

## Configuration

The project uses YAML files for configuration:

- `config/agents.yaml`: Define agent personas
- `config/tasks.yaml`: Configure tasks for agents
- `config/tools.yaml`: Set up tools for web search and vector DB

## Project Structure

```text
korean-language-chatbot/
├── config/               # Configuration files
│   ├── agents.yaml
│   ├── tasks.yaml
│   └── tools.yaml
├── src/                  # Source code
│   ├── agents/           # Agent definitions
│   └── tools/            # Tools for agents
├── text/                 # Raw text data
├── processed_chunks/     # Processed text chunks
├── docker-compose.yaml   # Docker composition
├── Dockerfile            # Container definition
├── process_text_data.py  # Text processing script
├── populate_qdrant.py    # Database population script
├── main.py               # Main entry point
└── README.md             # This file
```

## Acknowledgments

- CrewAI for the multi-agent framework
- Qdrant for vector database
- Ollama for local LLM capabilities
