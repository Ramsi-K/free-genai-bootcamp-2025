import os
import json
import time
import random
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import numpy as np
import chromadb
from chromadb.utils import embedding_functions
import asyncio
import torch
from functools import wraps

# Import OPEA components
from comps import MicroService, ServiceOrchestrator, ServiceType, ServiceRoleType
from comps.cores.proto.api_protocol import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatMessage,
    UsageInfo,
)
from comps.cores.proto.docarray import LLMParams, RerankerParms, RetrieverParms
from comps.cores.mega.utils import handle_message
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import Ollama

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
DATA_DIR = os.environ.get('DATA_DIR', '/shared/data')
CHROMA_DIR = os.environ.get('CHROMA_DIR', '/shared/data/chroma')
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://ollama:11434')
LLM_MODEL = os.environ.get('LLM_MODEL', 'llama3:8b')
TEI_HOST = os.environ.get('TEI_HOST', 'http://tei-embedding-service')
TEI_PORT = os.environ.get('TEI_PORT', '80')

# GPU Configuration
USE_GPU = os.environ.get('USE_GPU', 'true').lower() == 'true'
if USE_GPU and torch.cuda.is_available():
    DEVICE = torch.device("cuda")
    logger.info("Using GPU for LLM/Embedding processing")
else:
    DEVICE = torch.device("cpu")
    logger.info("Using CPU for LLM/Embedding processing")

# Create directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

# Initialize ServiceOrchestrator with GPU config
service_orchestrator = ServiceOrchestrator(device=DEVICE)

# Define OPEA microservices
embedding_service = MicroService(
    name="embedding",
    host=TEI_HOST,
    port=int(TEI_PORT),
    endpoint="/embed",
    use_remote_service=True,
    service_type=ServiceType.EMBEDDING,
    device=DEVICE
)

llm_service = MicroService(
    name="llm",
    host=OLLAMA_HOST.replace("http://", ""),  # Remove http:// prefix
    port=11434,
    endpoint="/api/generate",
    use_remote_service=True,
    service_type=ServiceType.LLM,
    device=DEVICE
)

# Add services to orchestrator
service_orchestrator.add(embedding_service)
service_orchestrator.add(llm_service)

# Add proper error handling for service operations
def safe_service_operation(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ServiceException as e:
            logger.error(f"Service operation failed: {str(e)}")
            raise
    return wrapper

# Define alignment functions similar to ChatQnA
@safe_service_operation
async def align_inputs(self, inputs, cur_node, runtime_graph, llm_parameters_dict, **kwargs):
    if self.services[cur_node].service_type == ServiceType.EMBEDDING:
        inputs["inputs"] = inputs["text"]
        del inputs["text"]
    elif self.services[cur_node].service_type == ServiceType.LLM:
        next_inputs = {}
        next_inputs["model"] = LLM_MODEL
        next_inputs["prompt"] = inputs["text"]
        next_inputs["stream"] = False
        next_inputs["temperature"] = llm_parameters_dict.get("temperature", 0.7)
        next_inputs["max_tokens"] = llm_parameters_dict.get("max_tokens", 512)
        inputs = next_inputs
    return inputs

@safe_service_operation
async def align_outputs(self, data, cur_node, inputs, runtime_graph, llm_parameters_dict, **kwargs):
    next_data = {}
    if self.services[cur_node].service_type == ServiceType.EMBEDDING:
        assert isinstance(data, list)
        next_data = {"text": inputs["inputs"], "embedding": data[0]}
    elif self.services[cur_node].service_type == ServiceType.LLM:
        next_data["text"] = data.get("response", "")
    else:
        next_data = data
    return next_data

# Assign alignment functions
ServiceOrchestrator.align_inputs = align_inputs
ServiceOrchestrator.align_outputs = align_outputs

# Setup ChromaDB
def setup_chroma():
    try:
        # Use sentence transformers embedding function with Korean model if available
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="jhgan/ko-sroberta-multitask"
        )
    except:
        # Fallback to default model
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    
    try:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        collection = client.get_or_create_collection(
            name="korean_transcripts", 
            embedding_function=embedding_function,
            metadata={"hnsw:space": "cosine"}
        )
        return client, collection
    except Exception as e:
        logger.error(f"Error setting up ChromaDB: {e}")
        raise

# Initialize ChromaDB
try:
    chroma_client, collection = setup_chroma()
    logger.info("ChromaDB initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize ChromaDB: {e}")
    # We'll try to initialize later

# Question generation prompt template
question_template = """
당신은 한국어 청취능력을 평가하는 TOPIK 시험 문제를 만드는 전문가입니다.
주어진 한국어 텍스트를 바탕으로 청취 이해력을 테스트하는 문제를 만들어야 합니다.

지문:
{text}

다음 지침에 따라 문제를 생성하세요:
1. 위 지문의 내용에 관한 객관식 문제를 1개 만드세요.
2. 각 문제는 질문과 4개의 선택지(가, 나, 다, 라)로 구성되어야 합니다.
3. 선택지 중 하나만 정답이어야 합니다.
4. 문제는 지문의 핵심 내용을 이해했는지 테스트해야 합니다.
5. 선택지는 서로 유사하되 명확히 구분될 수 있어야 합니다.
6. 정답을 표시하세요.

결과는 다음 JSON 형식으로 출력하세요:
```json
{
  "question": "질문 내용",
  "options": {
    "가": "첫 번째 선택지",
    "나": "두 번째 선택지",
    "다": "세 번째 선택지",
    "라": "네 번째 선택지"
  },
  "correct_answer": "정답 (가, 나, 다, 라 중 하나)",
  "explanation": "이 답이 정답인 이유에 대한 간단한 설명"
}
```

반드시 위의 형식으로 응답해야 합니다. 질문과 선택지는 모두 한국어로 작성하세요.
"""

# Define the prompt template for LLM
prompt = PromptTemplate(
    input_variables=["text"],
    template=question_template
)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

@app.route('/api/videos', methods=['GET'])
def list_videos():
    """List all videos with transcripts."""
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
        videos = []
        
        for file in files:
            file_path = os.path.join(DATA_DIR, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    videos.append({
                        'video_id': data.get('video_id'),
                        'title': data.get('metadata', {}).get('title', 'Unknown'),
                        'segments_count': len(data.get('segments', [])),
                        'processed_date': os.path.getmtime(file_path)
                    })
            except Exception as e:
                logger.error(f"Error reading file {file}: {e}")
        
        return jsonify({
            'success': True,
            'count': len(videos),
            'videos': videos
        })
    
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/index-video/<video_id>', methods=['POST'])
def index_video(video_id):
    """Index a video's transcript segments into ChromaDB."""
    try:
        # Try to initialize ChromaDB if it failed earlier
        if 'collection' not in globals():
            global chroma_client, collection
            chroma_client, collection = setup_chroma()
        
        file_path = os.path.join(DATA_DIR, f"{video_id}.json")
        if not os.path.exists(file_path):
            return jsonify({'error': 'Video not found'}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        segments = data.get('segments', [])
        if not segments:
            return jsonify({'error': 'No segments found in video data'}), 400
        
        # Add segments to ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for idx, segment in enumerate(segments):
            segment_id = f"{video_id}_segment_{idx}"
            
            documents.append(segment['text'])
            metadatas.append({
                'video_id': video_id,
                'segment_id': segment_id,
                'start': segment['start'],
                'end': segment['end'],
                'duration': segment['duration']
            })
            ids.append(segment_id)
        
        # Add to ChromaDB
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return jsonify({
            'success': True,
            'message': f"Successfully indexed {len(segments)} segments from video {video_id}",
            'segments_count': len(segments)
        })
    
    except Exception as e:
        logger.error(f"Error indexing video {video_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search_transcripts():
    """Search transcript segments using vector similarity."""
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        n_results = data.get('n_results', 5)
        
        # Search in ChromaDB
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        for idx, doc_id in enumerate(results['ids'][0]):
            metadata = results['metadatas'][0][idx]
            document = results['documents'][0][idx]
            formatted_results.append({
                'id': doc_id,
                'text': document,
                'metadata': metadata,
                'score': results['distances'][0][idx] if 'distances' in results else None
            })
        
        return jsonify({
            'success': True,
            'results': formatted_results
        })
    
    except Exception as e:
        logger.error(f"Error searching transcripts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-questions/<video_id>', methods=['POST'])
def generate_questions(video_id):
    """Generate questions for a specific video or segment using OPEA."""
    try:
        data = request.json or {}
        segment_ids = data.get('segment_ids', [])
        num_questions = data.get('num_questions', 3)
        
        file_path = os.path.join(DATA_DIR, f"{video_id}.json")
        if not os.path.exists(file_path):
            return jsonify({'error': 'Video not found'}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            video_data = json.load(f)
        
        segments = video_data.get('segments', [])
        if not segments:
            return jsonify({'error': 'No segments found in video data'}), 400
        
        # If specific segments are requested, use them
        if segment_ids:
            selected_segments = [segments[int(idx)] for idx in segment_ids if int(idx) < len(segments)]
        else:
            # Otherwise, randomly select segments
            if num_questions >= len(segments):
                selected_segments = segments
            else:
                selected_segments = random.sample(segments, num_questions)
        
        # Generate questions using OPEA
        questions = []
        for segment in selected_segments:
            try:
                segment_text = segment['text']
                prompt_text = question_template.format(text=segment_text)
                
                # Set up LLM parameters
                llm_parameters = LLMParams(
                    max_tokens=512,
                    temperature=0.7,
                    top_p=0.95,
                    stream=False,
                )
                
                # Create async loop for OPEA
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Schedule the OPEA orchestration
                result_dict, runtime_graph = loop.run_until_complete(
                    service_orchestrator.schedule(
                        initial_inputs={"text": prompt_text},
                        llm_parameters=llm_parameters
                    )
                )
                
                # Close the loop
                loop.close()
                
                # Get result from the last node
                last_node = runtime_graph.all_leaves()[-1]
                response = result_dict[last_node]["text"]
                
                # Extract JSON from response
                json_part = response.strip()
                if "```json" in json_part:
                    json_part = json_part.split("```json")[1].split("```")[0].strip()
                
                question_data = json.loads(json_part)
                
                # Add metadata to question
                question_data['segment'] = {
                    'start': segment['start'],
                    'end': segment['end'],
                    'duration': segment['duration'],
                    'text': segment['text']
                }
                
                questions.append(question_data)
                
            except Exception as e:
                logger.error(f"Error generating question for segment: {e}")
                # Continue with next segment if one fails
        
        # Create questions document
        questions_doc = {
            'video_id': video_id,
            'metadata': video_data.get('metadata', {}),
            'questions': questions,
            'generated_at': time.time()
        }
        
        # Save questions to file
        output_path = os.path.join(DATA_DIR, f"{video_id}_questions.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(questions_doc, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'questions_count': len(questions),
            'questions': questions
        })
    
    except Exception as e:
        logger.error(f"Error generating questions for video {video_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/questions/<video_id>', methods=['GET'])
def get_questions(video_id):
    """Get previously generated questions for a video."""
    try:
        questions_path = os.path.join(DATA_DIR, f"{video_id}_questions.json")
        if not os.path.exists(questions_path):
            return jsonify({'error': 'No questions found for this video'}), 404
        
        with open(questions_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        return jsonify({
            'success': True,
            'data': questions_data
        })
    
    except Exception as e:
        logger.error(f"Error getting questions for video {video_id}: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
