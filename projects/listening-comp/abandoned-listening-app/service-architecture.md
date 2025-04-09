# Korean Listening Comprehension MegaService Architecture

```mermaid
graph TB
    subgraph "OPEA MegaService"
        subgraph "transcript-processor"
            TP[Transcript Processor :5000]
            YT[YouTube API]
            TP --> YT
        end

        subgraph "question-module"
            QG[Question Generator :5001]
            EMB[Embedding Service]
            LLM[LLM Service]
            DB[(ChromaDB)]
            QG --> EMB
            QG --> LLM
            QG --> DB
        end

        subgraph "audio-module"
            TTS[Text-to-Speech :5002]
            AP[Audio Processor]
            TTS --> AP
        end

        subgraph "External Services"
            TEI[TEI Embedding :8080]
            OLLAMA[Ollama LLM :11434]
        end
    end

    %% Data flow with shared volume
    TP -- "Transcript Data" --> QG
    QG -- "Questions" --> TTS
    TTS -- "Audio Files" --> AP
    QG -- "Embeddings" --> TEI
    QG -- "LLM Requests" --> OLLAMA

    %% Shared storage connections
    SV[(Shared Volume)]
    TP --- SV
    QG --- SV
    TTS --- SV

    %% Styling
    classDef service fill:#f9f,stroke:#333,stroke-width:2px
    classDef external fill:#bbf,stroke:#333,stroke-width:2px
    classDef storage fill:#dfd,stroke:#333,stroke-width:2px

    class TP,QG,TTS service
    class TEI,OLLAMA external
    class SV,DB storage

```

Key Components:

1. Transcript Processor (Port 5000):

   - Handles YouTube video processing
   - Extracts and segments Korean transcripts
   - Communicates with question module

2. Question Module (Port 5001):

   - Generates questions using LLM
   - Stores embeddings in ChromaDB
   - Integrates with Ollama and TEI services

3. Audio Module (Port 5002):

   - Converts text to speech
   - Handles audio file management
   - Uses Korean TTS model

4. External Services:

   - TEI Embedding Service (Port 8080)
   - Ollama LLM Service (Port 11434)

5. Shared Resources:
   - Volume mounted at /shared/data
   - Persistent storage for all services
   - ChromaDB for vector storage

Data Flow:

1. Video URL → Transcript Processor
2. Transcript → Question Generator
3. Questions → TTS Service
4. Audio Files → Client

OPEA Integration:

- All services use ServiceOrchestrator
- Standardized request/response protocols
- Shared volume for data persistence
- Health monitoring enabled
