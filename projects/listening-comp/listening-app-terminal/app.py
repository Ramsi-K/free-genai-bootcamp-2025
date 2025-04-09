import os
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
import re
import nltk
import json
import hashlib
from translate import Translator

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

# Properly load models with exception handling
def load_text_generation_pipeline(model_key="gpt2"):
    """Load a text generation pipeline with proper error handling"""
    try:
        # Get model name from our model list
        model_info = MODELS.get(model_key, MODELS["gpt2"])
        model_name = model_info["name"]
        
        # Initialize tokenizer first to set pad_token_id properly
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Fix for GPT-2 warning about pad_token_id
        # Set pad_token to eos_token if it doesn't exist
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Create pipeline with configured tokenizer
        return pipeline('text-generation', 
                        model=model_name,
                        tokenizer=tokenizer,
                        max_length=800)
    except Exception as e:
        print(f"Error loading pipeline model: {e}")
        return None

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
        print(f"Error loading tokenizer and model: {e}")
        return None, None

def load_translation_model(model_key="gpt2"):
    """Load a model optimized for Korean to English translation."""
    try:
        # We'll try to use EXAONE for translation if available as it's better for Korean
        if model_key == 'exaone':
            tokenizer, model = load_tokenizer_and_model('exaone')
            if tokenizer is not None and model is not None:
                return 'exaone', tokenizer, model
        
        # Fallback to GPT-2 for translation
        generator = load_text_generation_pipeline('gpt2')
        if generator is not None:
            return 'gpt2', generator, None
        
        # If nothing is available
        return None, None, None
    except Exception as e:
        print(f"Error loading translation model: {e}")
        return None, None, None

def translate_korean_to_english(korean_text, use_streamlit=False):
    """Translate Korean text to English using the best available model.
    
    Args:
        korean_text: The Korean text to translate
        use_streamlit: If False (default), use print for messages instead of streamlit
    """
    try:
        # Load translation model if not already loaded
        model_type, model_or_tokenizer, model = load_translation_model()
        
        if model_type == 'exaone' and model_or_tokenizer is not None and model is not None:
            try:
                # Use EXAONE model for better Korean translation
                print("Using EXAONE model for translation...")
                
                # Tokenizer is stored in model_or_tokenizer, model in model
                tokenizer = model_or_tokenizer
                
                messages = [
                    {"role": "system", "content": "You are a helpful Korean to English translator."},
                    {"role": "user", "content": f"Translate the following Korean text to English. Only respond with the translation, no additional text:\n\n{korean_text}"}
                ]
                
                # Tokenize with the model we have
                input_ids = tokenizer.apply_chat_template(
                    messages,
                    tokenize=True,
                    add_generation_prompt=True,
                    return_tensors="pt"
                )
                
                if torch.cuda.is_available():
                    input_ids = input_ids.to("cuda")
                
                # Generate translation
                output = model.generate(
                    input_ids,
                    max_new_tokens=256,
                    do_sample=False
                )
                
                translation = tokenizer.decode(output[0], skip_special_tokens=True)
                
                # Extract only the translated part by removing prompt text
                if "Translate the following Korean text to English" in translation:
                    translation = translation.split("Translate the following Korean text to English")[1]
                if korean_text in translation:
                    translation = translation.split(korean_text, 1)[1].strip()
                
                # Clean up translation result
                if "English translation:" in translation.lower():
                    translation = translation.split("English translation:", 1)[1].strip()
                
                # Remove any remaining system/user prompt residue
                translation = re.sub(r'^[Ss]ystem:.*?\n', '', translation)
                translation = re.sub(r'^[Uu]ser:.*?\n', '', translation)
                translation = re.sub(r'^[Aa]ssistant:.*?\n', '', translation)
                
                return translation.strip()
            
            except Exception as e:
                print(f"EXAONE translation failed: {e}")
        
        elif model_type == 'gpt2' and model_or_tokenizer is not None:
            try:
                # Use GPT-2 pipeline
                generator = model_or_tokenizer
                print("Using GPT-2 for translation...")
                
                prompt = f"Translate this Korean text to English: {korean_text}\nEnglish translation:"
                result = generator(prompt, 
                            num_return_sequences=1,
                            max_length=150,
                            do_sample=True,
                            temperature=0.7,
                            truncation=True,
                            # Suppress warnings by explicitly stating we're handling pad token
                            pad_token_id=generator.tokenizer.pad_token_id)[0]['generated_text']
                
                # Extract the translation part
                if "English translation:" in result:
                    translation = result.split("English translation:", 1)[1].strip()
                    return translation
                else:
                    # Try to extract anything after the Korean text
                    if korean_text in result:
                        translation = result.split(korean_text, 1)[1].strip()
                        return translation
                    else:
                        return result  # Return full result if can't extract cleanly
            
            except Exception as e:
                print(f"GPT-2 translation failed: {e}")
        
        # Fallback to simple translator
        print("Using simple translator...")
        translator = Translator(to_lang="en")
        translation = translator.translate(korean_text)
        return translation
        
    except Exception as e:
        print(f"Translation error: {e}")
        return f"Translation failed. Original text: {korean_text}"

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
                        print(f"Loaded {len(cached_questions)} TOPIK-style questions from cache.")
                        return cached_questions
            except Exception as e:
                print(f"Error loading cached questions: {e}")
        
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
            generator = load_text_generation_pipeline(model_choice)
            if generator is None:
                print("Failed to load GPT-2 model.")
                return []
                
            try:
                result = generator(prompt, 
                            num_return_sequences=1,
                            do_sample=True,
                            top_k=50,
                            top_p=0.95,
                            temperature=0.7,
                            truncation=True)[0]['generated_text']
            except Exception as e:
                print(f"Error during GPT-2 generation: {e}")
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
                
                # Load model and tokenizer
                tokenizer, model = load_tokenizer_and_model(model_choice)
                
                # Check if tokenizer and model were loaded successfully
                if tokenizer is None or model is None:
                    print("EXAONE model or tokenizer not available.")
                    # Fall back to GPT-2
                    print("Falling back to GPT-2 model...")
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
                print(f"Error during EXAONE processing: {e}")
                # Fall back to GPT-2
                print("Falling back to GPT-2 model...")
                return generate_topik_questions_with_llm(transcript, num_questions, "gpt2", difficulty)
        
        # Parse the generated questions 
        questions = parse_generated_questions(result)
        
        # Cache the questions for future use
        if questions:
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(questions, f, ensure_ascii=False, indent=2)
                print(f"Cached {len(questions)} TOPIK-style questions for future use.")
            except Exception as e:
                print(f"Error caching questions: {e}")
        
        return questions
        
    except Exception as e:
        print(f"Error generating TOPIK-style questions with LLM: {e}")
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
                print(f"Error parsing question block: {e}")
                continue
    
    except Exception as e:
        print(f"Error parsing generated questions: {e}")
    
    return questions

# Initialize models for common use
_generator = None
_tokenizer = None
_model = None

def initialize_models(model_name="gpt2"):
    """Initialize models for use in the application"""
    global _generator, _tokenizer, _model
    
    try:
        if model_name == "gpt2":
            _generator = load_text_generation_pipeline("gpt2")
            _tokenizer, _model = None, None
        else:  # EXAONE or other complex model
            _generator = None  # Don't use pipeline for these models
            _tokenizer, _model = load_tokenizer_and_model(model_name)
        
        return True
    except Exception as e:
        print(f"Error during model initialization: {e}")
        return False