# Korean Language Learning Adventure Game

A colorful, interactive text adventure game designed to teach Korean vocabulary words to beginners.

## Prerequisites

- Python 3.6+
- [Ollama](https://ollama.com/) - A local LLM server

## Setup Instructions

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Set up Ollama**

Download and install Ollama from [ollama.com](https://ollama.com/).

3. **Start the Ollama server**

```bash
ollama serve
```

4. **Pull your preferred Korean language model**

```bash
ollama pull kimjk/llama3.2-korean:latest
```

You can use any language model that supports Korean. The default is `kimjk/llama3.2-korean:latest`.

## Customizing the Model

To use a different model, edit the `MODEL` variable at the top of `dynamic-korean-adventure.py`:

```python
MODEL = "your-preferred-model"  # Change this to your model of choice
```

## Running the Game

```bash
python dynamic-korean-adventure.py
```

If you're using Docker or a different host for Ollama, you can specify the URL:

```bash
python dynamic-korean-adventure.py http://your-ollama-url:11434
```

## How to Play

- Use natural language commands to interact with the game world
- Basic commands: look, move, take, talk, use, give, inventory, help
- Each interaction teaches you a new Korean word
- Explore rooms, collect items, and talk to characters

## Game Features

- Colorful terminal UI with Unicode formatting
- Dynamic world generation using the LLM
- Korean vocabulary learning with pronunciation guides
- Progress tracking for learned words
- Natural language understanding for commands

## Troubleshooting

If you encounter connection issues:

1. Make sure Ollama is running with `ollama serve`
2. Verify your model is downloaded with `ollama list`
3. Check that port 11434 is accessible
4. If using Docker, ensure proper port mapping
