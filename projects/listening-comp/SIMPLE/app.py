import streamlit as st
import time
from pathlib import Path
import os
import shutil
import csv
import sounddevice as sd
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from datetime import datetime
import random
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
import re
import nltk
from nltk.tokenize import word_tokenize
import json
import hashlib

# Initialize NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Define directories
MODEL_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_cache")
QUESTION_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "question_cache")
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
os.makedirs(QUESTION_CACHE_DIR, exist_ok=True)

# Model information
MODELS = {
    "gpt2": {
        "name": "gpt2",
        "display_name": "GPT-2 (English base, small ~500MB)",
        "description": "Fast to download and run, less accurate for Korean",
        "size": "~500MB",
        "korean_support": "Limited"
    },
    "exaone": {
        "name": "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct",
        "display_name": "EXAONE-3.5-2.4B (Korean/English, large)",
        "description": "High quality Korean language support, but large download",
        "size": "~2.4GB",
        "korean_support": "Excellent"
    }
}

# Store model choice in session state
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = "gpt2"  # Default model
model_name = st.session_state['model_name']

# Properly load models with exception handling
@st.cache_resource
def load_text_generation_pipeline(model_key="gpt2"):
    """Load a text generation pipeline with proper error handling"""
    try:
        # Get model name from our model list
        model_info = MODELS.get(model_key, MODELS["gpt2"])
        model_name = model_info["name"]
        
        # Don't pass cache_dir directly to pipeline as it causes errors
        return pipeline('text-generation', 
                        model=model_name,
                        max_length=800)
    except Exception as e:
        st.error(f"Error loading pipeline model: {e}")
        return None

@st.cache_resource
def load_tokenizer_and_model(model_key="exaone"):
    """Load a tokenizer and model for more complex models with proper error handling"""
    try:
        # Get model name from our model list
        model_info = MODELS.get(model_key, MODELS["exaone"]) 
        model_name = model_info["name"]
        
        # Load tokenizer with cache
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Load model with appropriate settings
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
            trust_remote_code=True,
            device_map="auto"
        )
        
        return tokenizer, model
    except Exception as e:
        st.error(f"Error loading tokenizer and model: {e}")
        return None, None

# Load generators based on user preference
try:
    if model_name == "gpt2":
        generator = load_text_generation_pipeline("gpt2")
        tokenizer, model = None, None
    else:  # EXAONE or other complex model
        generator = None  # Don't use pipeline for these models
        tokenizer, model = load_tokenizer_and_model(model_name)
except Exception as e:
    st.error(f"Error during model initialization: {e}")
    generator, tokenizer, model = None, None, None

def generate_topik_questions_with_llm(transcript, num_questions=3, model_choice="gpt2", difficulty="medium"):
    """Generate TOPIK-style questions with proper error handling"""
    try:
        # Get model details
        model_info = MODELS.get(model_choice, MODELS["gpt2"])
        model_name = model_info["name"]
        
        # Check if we have cached questions for this transcript, model and difficulty
        transcript_hash = hashlib.md5(transcript.encode('utf-8')).hexdigest()
        cache_file = os.path.join(QUESTION_CACHE_DIR, f"{model_choice}_{difficulty}_{transcript_hash}_{num_questions}.json")
        
        # Try to load cached questions first
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_questions = json.load(f)
                    if cached_questions and len(cached_questions) > 0:
                        st.success(f"Loaded {len(cached_questions)} TOPIK-style questions from cache.")
                        return cached_questions
            except Exception as e:
                st.warning(f"Error loading cached questions: {e}")
        
        # Prepare transcript - limit to reduce token length
        # Using a smaller excerpt to avoid token limits
        transcript_excerpt = transcript[:800] if len(transcript) > 800 else transcript
        
        if model_choice == "gpt2":
            # Create prompt for GPT-2 with difficulty adjustments
            if difficulty == "easy":
                complexity = "simple and basic"
            elif difficulty == "hard":
                complexity = "challenging and advanced"
            else:
                complexity = "intermediate"
                
            prompt = f"""Generate {num_questions} {complexity} TOPIK-style listening comprehension questions based on this Korean transcript:

{transcript_excerpt}

For each question:
1. Create a short Korean sentence (under 30 words) that could be from the transcript
2. Create a question about that sentence/concept
3. Provide 4 possible answers (A, B, C, D) with one correct answer
4. Mark the correct answer

Format each question EXACTLY as:
SENTENCE: [Korean sentence to be played as audio]
QUESTION: [Question in Korean about the sentence]
OPTIONS:
A. [Option A in Korean]
B. [Option B in Korean]
C. [Option C in Korean]
D. [Option D in Korean]
CORRECT: [Correct option letter]

"""
            # Generate using pipeline
            try:
                result = generator(prompt, 
                            num_return_sequences=1,
                            do_sample=True,
                            top_k=50,
                            top_p=0.95,
                            temperature=0.7,
                            truncation=True)[0]['generated_text']
            except Exception as e:
                st.error(f"Error during GPT-2 generation: {e}")
                return []
                
        else:  # EXAONE model
            # Adjust complexity based on difficulty
            difficulty_text = ""
            if difficulty == "easy":
                difficulty_text = "쉬운 초급"  # Easy/beginner level
            elif difficulty == "hard":
                difficulty_text = "어려운 고급"  # Difficult/advanced level
            else:
                difficulty_text = "중급"  # Intermediate level
                
            # Korean prompt for better results
            prompt = f"""다음 한국어 텍스트를 바탕으로 {difficulty_text} 수준의 TOPIK 듣기 이해 문제를 {num_questions}개 생성해 주세요:

{transcript_excerpt}

각 문제에 대해:
1. 텍스트에서 짧은 한국어 문장을 선택하거나 만드세요 (30단어 이내)
2. 그 문장에 대한 이해 질문을 만드세요
3. 4가지 선택지(A, B, C, D)를 제공하고 정답을 표시하세요

반드시 다음 형식으로 각 질문을 작성해 주세요:
SENTENCE: [오디오로 재생될 문장]
QUESTION: [문장에 대한 질문]
OPTIONS:
A. [선택지 A]
B. [선택지 B]
C. [선택지 C]
D. [선택지 D]
CORRECT: [정답 옵션의 알파벳]
"""
            
            try:
                # Prepare messages
                messages = [
                    {"role": "system", 
                     "content": "You are EXAONE model from LG AI Research, a helpful Korean language assistant specialized in creating TOPIK-style listening questions."},
                    {"role": "user", "content": prompt}
                ]
                
                # Check if tokenizer and model were loaded successfully
                if tokenizer is None or model is None:
                    st.error("EXAONE model or tokenizer not available.")
                    # Fall back to GPT-2
                    st.warning("Falling back to GPT-2 model...")
                    return generate_topik_questions_with_llm(transcript, num_questions, "gpt2", difficulty)
                
                # Tokenize
                input_ids = tokenizer.apply_chat_template(
                    messages,
                    tokenize=True,
                    add_generation_prompt=True,
                    return_tensors="pt"
                ).to(model.device)
                
                # Generate
                output = model.generate(
                    input_ids,
                    eos_token_id=tokenizer.eos_token_id,
                    max_new_tokens=1024,
                    do_sample=False,
                )
                
                result = tokenizer.decode(output[0], skip_special_tokens=True)
            except Exception as e:
                st.error(f"Error during EXAONE processing: {e}")
                # Fall back to GPT-2
                st.warning("Falling back to GPT-2 model...")
                return generate_topik_questions_with_llm(transcript, num_questions, "gpt2", difficulty)
        
        # Parse the generated questions 
        questions = parse_generated_questions(result)
        
        # Cache the questions for future use
        if questions:
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(questions, f, ensure_ascii=False, indent=2)
                st.success(f"Cached {len(questions)} TOPIK-style questions for future use.")
            except Exception as e:
                st.warning(f"Error caching questions: {e}")
        
        return questions
        
    except Exception as e:
        st.error(f"Error generating TOPIK-style questions with LLM: {e}")
        return []

def parse_generated_questions(generated_text):
    """Parse generated TOPIK-style questions from LLM output."""
    questions = []
    
    try:
        # Extract question blocks - look for SENTENCE: pattern
        pattern = r'SENTENCE:\s*(.*?)(?=SENTENCE:|$)'
        question_blocks = re.findall(pattern, generated_text, re.DOTALL)
        
        for block in question_blocks:
            try:
                # Extract sentence
                sentence_match = re.search(r'SENTENCE:\s*(.*?)(?=QUESTION:|$)', block, re.DOTALL)
                sentence = sentence_match.group(1).strip() if sentence_match else ""
                
                if not sentence:  # Skip if no sentence found
                    continue
                
                # Extract question text
                question_match = re.search(r'QUESTION:\s*(.*?)(?=OPTIONS:|$)', block, re.DOTALL)
                question_text = question_match.group(1).strip() if question_match else ""
                
                # Extract options
                options = []
                options_match = re.search(r'OPTIONS:(.*?)(?=CORRECT:|$)', block, re.DOTALL)
                if options_match:
                    options_text = options_match.group(1)
                    option_pattern = r'([A-D])\.\s*(.*?)(?=[A-D]\.|CORRECT:|$)'
                    option_matches = re.findall(option_pattern, options_text, re.DOTALL)
                    options = [opt[1].strip() for opt in option_matches]
                
                # Extract correct answer
                correct_match = re.search(r'CORRECT:\s*([A-D])', block)
                correct_option = correct_match.group(1) if correct_match else ""
                
                if sentence and question_text and len(options) == 4 and correct_option:
                    questions.append({
                        "sentence": sentence,
                        "question_text": question_text,
                        "options": options,
                        "correct_option": correct_option
                    })
            except Exception as e:
                st.warning(f"Error parsing question block: {e}")
                continue
    
    except Exception as e:
        st.error(f"Error parsing generated questions: {e}")
    
    return questions

# Main app structure - placeholder for the actual app implementation
def main():
    st.title("Korean Listening Practice App")
    
    # Model selection in sidebar
    with st.sidebar:
        st.subheader("Model Options")
        model_option = st.selectbox(
            "Choose LLM model for question generation:",
            options=["gpt2", "exaone"],
            format_func=lambda x: MODELS[x]["display_name"],
            index=0
        )
        
        if model_option != st.session_state.get('model_name'):
            st.session_state['model_name'] = model_option
            st.warning(f"Model changed to {MODELS[model_option]['display_name']}. Please reload the app.")
            st.rerun()

    # Rest of the app implementation would go here
    # ...existing code...