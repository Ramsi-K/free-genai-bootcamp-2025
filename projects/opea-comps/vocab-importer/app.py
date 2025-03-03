from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import os
import logging
from typing import List, Optional, Dict, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Korean Vocabulary Importer")

# Get the vLLM service URL from environment variables
VLLM_SERVICE_URL = os.getenv("VLLM_SERVICE_URL", "http://vllm-server:80")
logger.info(f"Using LLM service at: {VLLM_SERVICE_URL}")

class ExampleSentence(BaseModel):
    korean: str
    english: str

class VocabWord(BaseModel):
    hangul: str
    romanization: str
    type: Optional[str] = None
    english: List[str]
    example_sentence: Optional[ExampleSentence] = None

class VocabGroup(BaseModel):
    name: str
    description: str
    words: List[VocabWord]

class VocabGenerationRequest(BaseModel):
    theme: str
    count: int = 10
    include_example_sentences: bool = True

# In-memory storage for demo purposes
# In production, use a database
vocab_groups = []

# Fallback data for when the LLM service is unavailable
def get_fallback_data(theme):
    return {
        "name": theme,
        "description": f"Words related to {theme} in Korean",
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
            },
            {
                "hangul": "밥",
                "romanization": "bap",
                "type": "noun",
                "english": ["rice", "meal"],
                "example_sentence": {
                    "korean": "저는 매일 아침에 밥을 먹어요.",
                    "english": "I eat rice every morning."
                }
            },
            {
                "hangul": "국수",
                "romanization": "guksu",
                "type": "noun",
                "english": ["noodles"],
                "example_sentence": {
                    "korean": "더운 날에는 차가운 국수가 맛있어요.",
                    "english": "Cold noodles are delicious on hot days."
                }
            }
        ]
    }

@app.post("/generate", response_model=VocabGroup)
async def generate_vocabulary(request: VocabGenerationRequest):
    # Construct prompt based on theme
    example_sentence_part = ""
    if request.include_example_sentences:
        example_sentence_part = """
            "example_sentence": {
                "korean": "Example sentence in Korean using the word",
                "english": "English translation of the example sentence"
            }
        """
    
    prompt = f"""Generate {request.count} Korean vocabulary words about '{request.theme}'. 
    Format the response as a valid JSON object with the following structure:
    {{
        "name": "{request.theme}",
        "description": "Words related to {request.theme} in Korean",
        "words": [
            {{
                "hangul": "Korean word in Hangul",
                "romanization": "Romanized version",
                "type": "noun/verb/adjective/etc.",
                "english": ["Primary meaning", "Alternative meaning if applicable"],
                {example_sentence_part}
            }}
        ]
    }}
    Ensure it's valid JSON. Include accurate romanization and appropriate part of speech (type).
    """

    # Try different vLLM API formats
    try:
        # First try the vLLM OpenAI-compatible API format
        logger.info(f"Attempting to connect to vLLM service at {VLLM_SERVICE_URL}")
        
        # Try the vLLM OpenAI-compatible API
        response = requests.post(
            f"{VLLM_SERVICE_URL}/v1/completions",
            json={
                "model": "microsoft/phi-2",  # This might be ignored by vLLM
                "prompt": prompt,
                "max_tokens": 1000,
                "temperature": 0.7
            },
            timeout=30
        )
        
        logger.info(f"vLLM API response status: {response.status_code}")
        
        if response.status_code == 200:
            llm_response = response.json()
            logger.info(f"LLM response keys: {llm_response.keys()}")
            
            # Try to extract the generated text
            if "choices" in llm_response and len(llm_response["choices"]) > 0:
                generated_text = llm_response["choices"][0].get("text", "")
                logger.info(f"Generated text (first 100 chars): {generated_text[:100]}")
                
                # Try to extract JSON from the generated text
                try:
                    json_start = generated_text.find("{")
                    json_end = generated_text.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = generated_text[json_start:json_end]
                        vocab_data = json.loads(json_str)
                        vocab_group = VocabGroup(**vocab_data)
                        
                        # Store in our in-memory database
                        vocab_groups.append(vocab_group)
                        return vocab_group
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from LLM response: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error calling vLLM service: {str(e)}")

    # If we get here, either the request failed or the response didn't contain valid data
    # Fall back to the sample data
    logger.info("Using fallback data")
    fallback_data = get_fallback_data(request.theme)
    vocab_group = VocabGroup(**fallback_data)
    vocab_groups.append(vocab_group)
    return vocab_group

@app.get("/groups", response_model=List[VocabGroup])
async def list_vocab_groups():
    return vocab_groups

@app.get("/export/{index}")
async def export_vocab_group(index: int):
    if index < 0 or index >= len(vocab_groups):
        raise HTTPException(status_code=404, detail="Vocab group not found")
    return vocab_groups[index]

@app.post("/import", response_model=VocabGroup)
async def import_vocab_group(vocab_group: VocabGroup):
    vocab_groups.append(vocab_group)
    return vocab_group

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
