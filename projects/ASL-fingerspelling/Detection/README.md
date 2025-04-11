# ASL Fingerspelling Practice App

An interactive web application to help users learn and practice American Sign Language (ASL) fingerspelling.

## Features

- Learn ASL fingerspelling with detailed descriptions and video demonstrations
- Practice signing letters with real-time feedback using AI recognition
- Test your skills with the fingerspelling test mode
- Track your progress as you learn

## Docker Setup

This project uses Docker to run both the web application and the Ollama service for AI recognition.

### Prerequisites

- Docker and Docker Compose installed on your system
- At least 4GB of RAM available for the Ollama service and model

### Running the Application

1. Clone this repository
2. Navigate to the project directory
3. Start the containers:

```bash
docker-compose up -d
```

4. Initialize Ollama and pull the Ishara model:

```bash
chmod +x init-ollama.sh
docker exec -it asl-web ./init-ollama.sh
```

5. Open your browser and navigate to:
   - http://localhost:8000/finger_spelling-practice.html for Practice mode
   - http://localhost:8000/finger-spelling-test.html for Test mode

### First-Time Setup Notes

The first time you run the application, it may take some time to download the Ishara model (around 2-3 GB). The application will be fully functional once the model download is complete.

## Usage

1. In Practice mode:

   - Click on any letter in the grid to see a detailed video demonstration
   - Use "Start Camera" to practice with your webcam
   - "Check My Sign" will use AI to see if your sign is correct

2. In Test mode:
   - The system will present random letters for you to sign
   - Follow the prompts and see if your signs are recognized correctly

## Troubleshooting

- If you get an "API error" when checking signs, make sure the Ollama service is running and the Ishara model has been successfully pulled.
- Camera not working? Make sure you've granted camera permissions to the application.

## Credits

- ASL videos: mirzamlk (https://www.shutterstock.com/g/mirzamlk/about)
- Ishara model: https://huggingface.co/TanmayNanda/ishara
