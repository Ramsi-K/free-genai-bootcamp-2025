import os
import re
import random
import tempfile
import json
import datetime
import hashlib
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import time
import pygame
import torch
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from gtts import gTTS
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

# Define model cache directory
MODEL_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_cache")
QUESTION_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "question_cache")

# Create directories if they don't exist
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

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def extract_youtube_id(url):
    """Extract video ID from various forms of YouTube URLs."""
    parsed_url = urlparse(url)
    if parsed_url.netloc == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.netloc in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            query = parse_qs(parsed_url.query)
            return query.get('v', [None])[0]
        if parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        if parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
    return None

def fetch_korean_transcript(video_id):
    """Get transcript using YouTubeTranscriptApi with better error handling for Korean transcripts."""
    try:
        # Try to get Korean transcript (manual or auto-generated)
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["ko"])
            return format_transcript(transcript)
        except Exception:
            pass

        # Try Korean (South Korea) subtitles
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["ko-KR"])
            return format_transcript(transcript)
        except Exception:
            pass

        print("Korean subtitles not found, please try another video.")
        return None

    except NoTranscriptFound:
        print("Korean subtitles not found, please try another video.")
        return None
    except TranscriptsDisabled:
        print("Korean subtitles not found, please try another video.")
        return None
    except Exception as e:
        print("An error occurred. Please try another video.")
        return None

def format_transcript(transcript):
    """Format transcript data into a string."""
    if not transcript:
        return None
        
    transcript_text = ""
    for entry in transcript:
        if isinstance(entry, dict) and 'text' in entry:
            transcript_text += entry['text'] + " "
    
    return transcript_text.strip()

def extract_sentences(transcript, num_sentences=5):
    """Extract a specified number of Korean sentences from the transcript."""
    if not transcript:
        return []
    
    # Split the transcript by sentence endings
    sentences = re.split(r'[.!?]\s+', transcript)
    
    # Filter out too short or too long sentences
    valid_sentences = [s for s in sentences if 10 <= len(s) <= 100]
    
    if not valid_sentences:
        return []
        
    # Select random sentences
    if len(valid_sentences) <= num_sentences:
        return valid_sentences
    else:
        return random.sample(valid_sentences, num_sentences)

def generate_questions(sentences):
    """Generate multiple-choice questions based on Korean sentences."""
    questions = []
    
    # Simple approach: Just remove random words and create options
    for sentence in sentences:
        words = sentence.split()
        if len(words) < 4:  # Skip if sentence is too short
            continue
            
        # Choose a random word to remove (avoid first or last word for context)
        word_index = random.randint(1, len(words) - 2)
        removed_word = words[word_index]
        
        # Create the sentence with a blank
        blank_sentence = ' '.join(words[:word_index]) + ' _____ ' + ' '.join(words[word_index+1:])
        
        # Generate distractors (other random Korean words from all sentences)
        all_words = []
        for s in sentences:
            all_words.extend(s.split())
        
        # Filter out the correct answer and short words
        potential_distractors = [w for w in all_words if w != removed_word and len(w) > 1]
        
        # If we don't have enough distractors, just use the removed word with slight variations
        if len(potential_distractors) < 3:
            distractors = [removed_word + "요", removed_word + "은", removed_word + "는"]
        else:
            distractors = random.sample(potential_distractors, 3)
        
        # Create options (A, B, C, D) with the correct answer included
        options = distractors + [removed_word]
        random.shuffle(options)
        
        # Find the correct answer's option letter
        correct_option = chr(65 + options.index(removed_word))  # A, B, C, or D
        
        questions.append({
            'sentence': sentence,
            'blank_sentence': blank_sentence,
            'removed_word': removed_word,
            'options': options,
            'correct_option': correct_option
        })
    
    return questions

def save_audio_file(text, filename):
    """Generate Korean text-to-speech audio and save to a file."""
    try:
        tts = gTTS(text=text, lang='ko', slow=False)
        tts.save(filename)
        return True
    except Exception as e:
        print(f"Error saving audio: {e}")
        return False

def text_to_speech(text, save_path=None):
    """Generate Korean text-to-speech audio and play it."""
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
    temp_filename = temp_file.name
    temp_file.close()
    
    try:
        # Generate TTS
        tts = gTTS(text=text, lang='ko', slow=False)
        tts.save(temp_filename)
        
        # Save to permanent location if requested
        if save_path:
            try:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(temp_filename, 'rb') as src_file:
                    with open(save_path, 'wb') as dst_file:
                        dst_file.write(src_file.read())
            except Exception as e:
                print(f"Error saving audio to {save_path}: {e}")
        
        # Initialize pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()
        
        # Wait for audio to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        return temp_filename if not save_path else save_path
    
    finally:
        # Cleanup temporary file if we're not saving it
        pygame.mixer.quit()
        if os.path.exists(temp_filename) and save_path:
            os.unlink(temp_filename)

def display_question(question, question_num, total_questions):
    """Display a question to the user."""
    clear_screen()
    print(f"\n🎧 Question {question_num} of {total_questions}\n")
    print(f"Listen to the following sentence:")
    print(f"\n{question['blank_sentence']}\n")
    
    # Display options
    for i, option in enumerate(question['options']):
        print(f"{chr(65 + i)}. {option}")
    
    print("\nPress 'R' to replay the audio.")

def create_quiz_session_dict(video_id, transcript, questions):
    """Create a dictionary of the quiz session data for storing in JSON."""
    session = {
        "video_id": video_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "transcript": transcript,
        "questions": []
    }
    
    for q in questions:
        question_data = {
            "sentence": q["sentence"],
            "blank_sentence": q["blank_sentence"],
            "removed_word": q["removed_word"],
            "options": q["options"],
            "correct_option": q["correct_option"],
            "audio_path": ""  # Will be filled later
        }
        session["questions"].append(question_data)
    
    return session

def save_quiz_session(session_data, base_dir="quiz_sessions"):
    """Save quiz session data and audio files."""
    # Create session directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    video_id = session_data["video_id"]
    session_dir = os.path.join(base_dir, f"{video_id}_{timestamp}")
    os.makedirs(session_dir, exist_ok=True)
    
    # Create audio directory
    audio_dir = os.path.join(session_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    # Save audio files for each question
    for i, question in enumerate(session_data["questions"]):
        audio_filename = f"question_{i+1}.mp3"
        audio_path = os.path.join(audio_dir, audio_filename)
        
        # Generate and save audio file
        save_audio_file(question["sentence"], audio_path)
        
        # Update the audio path in the session data
        session_data["questions"][i]["audio_path"] = os.path.relpath(audio_path, session_dir)
    
    # Save session data as JSON
    json_path = os.path.join(session_dir, "session_data.json")
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(session_data, json_file, ensure_ascii=False, indent=2)
    
    return json_path

def load_quiz_session(session_path):
    """Load a previously saved quiz session."""
    try:
        with open(session_path, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    except Exception as e:
        print(f"Error loading quiz session: {e}")
        return None

def quiz_user(questions, session_dir=None):
    """Quiz the user with the generated questions."""
    score = 0
    total = len(questions)
    
    for i, question in enumerate(questions):
        display_question(question, i+1, total)
        
        # Determine audio path
        audio_path = None
        if session_dir and "audio_path" in question and question["audio_path"]:
            audio_path = os.path.join(session_dir, question["audio_path"])
            if not os.path.exists(audio_path):
                audio_path = None
        
        # Play the audio for the full sentence
        if audio_path and os.path.exists(audio_path):
            # Play existing audio file
            pygame.mixer.init()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.quit()
        else:
            # Generate new audio
            text_to_speech(question['sentence'])
        
        while True:
            user_input = input("\nYour answer (A/B/C/D or R to replay): ").upper()
            
            if user_input == 'R':
                if audio_path and os.path.exists(audio_path):
                    pygame.mixer.init()
                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                    pygame.mixer.quit()
                else:
                    text_to_speech(question['sentence'])
                continue
                
            if user_input in ['A', 'B', 'C', 'D']:
                break
                
            print("Invalid input. Please enter A, B, C, D, or R.")
        
        if user_input == question['correct_option']:
            print("\n✅ Correct! The answer was: " + question['removed_word'])
            score += 1
        else:
            correct_word = question['removed_word']
            print(f"\n❌ Incorrect. The correct answer was {question['correct_option']}: {correct_word}")
        
        print("\nOriginal sentence:")
        print(f"{question['sentence']}")
        
        input("\nPress Enter to continue...")
    
    return score, total

def display_final_score(score, total):
    """Display the final score to the user."""
    clear_screen()
    print("\n=== 🏆 Final Score ===")
    print(f"\nYou got {score} out of {total} questions correct!")
    
    percentage = (score / total) * 100 if total > 0 else 0
    print(f"Your score: {percentage:.1f}%\n")
    
    if percentage >= 80:
        print("🌟 Outstanding! Your Korean listening skills are excellent!")
    elif percentage >= 60:
        print("👍 Good job! Keep practicing!")
    else:
        print("💪 Keep working on it! Practice makes perfect!")

def generate_topik_questions_with_llm(transcript, num_questions=3, model_choice="exaone"):
    """Use an LLM to generate TOPIK-style listening comprehension questions."""
    try:
        # Get model details
        model_info = MODELS.get(model_choice, MODELS["gpt2"])
        model_name = model_info["name"]
        
        # Check if we have cached questions for this transcript and model
        transcript_hash = hashlib.md5(transcript.encode('utf-8')).hexdigest()
        cache_file = os.path.join(QUESTION_CACHE_DIR, f"{model_choice}_{transcript_hash}_{num_questions}.json")
        
        # Try to load cached questions first
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_questions = json.load(f)
                    print(f"Loaded {len(cached_questions)} questions from cache.")
                    return cached_questions
            except Exception as e:
                print(f"Error loading cached questions: {e}")
        
        # If no cache or error, generate new questions
        print(f"Initializing {model_info['display_name']} for question generation...")
        
        if model_choice == "gpt2":
            # Use pipeline for simpler models
            generator = pipeline('text-generation', 
                               model=model_name,
                               max_length=800,
                               cache_dir=MODEL_CACHE_DIR)
            
            # Create prompt for GPT-2
            prompt = f"""Generate {num_questions} TOPIK-style listening comprehension questions based on this Korean transcript:

{transcript[:500]}...

For each question:
1. Extract a key sentence or concept from the transcript
2. Create a question about that sentence/concept
3. Provide 4 possible answers (A, B, C, D) with one correct answer
4. Mark the correct answer

Format each question as:
SENTENCE: [Korean sentence to be played as audio]
QUESTION: [Question in Korean about the sentence]
OPTIONS:
A. [Option A in Korean]
B. [Option B in Korean]
C. [Option C in Korean]
D. [Option D in Korean]
CORRECT: [Correct option letter]

"""
            # Generate questions using the pipeline
            result = generator(prompt, num_return_sequences=1)[0]['generated_text']
            
        else:  # EXAONE model
            # Load the model and tokenizer with cache directory
            tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=MODEL_CACHE_DIR)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.bfloat16,
                trust_remote_code=True,
                device_map="auto",
                cache_dir=MODEL_CACHE_DIR
            )
            
            # Prepare a prompt for the model
            prompt = f"""다음 한국어 텍스트에서 TOPIK 듣기 이해 문제를 {num_questions}개 생성해 주세요:

{transcript[:1000]}...

각 문제에 대해:
1. 텍스트에서 중요한 문장을 선택하세요
2. 그 문장에 대한 이해 질문을 만드세요
3. 4가지 선택지(A, B, C, D)를 제공하고 정답을 표시하세요

다음 형식으로 각 질문을 작성해 주세요:
SENTENCE: [오디오로 재생될 문장]
QUESTION: [문장에 대한 질문]
OPTIONS:
A. [선택지 A]
B. [선택지 B]
C. [선택지 C]
D. [선택지 D]
CORRECT: [정답 옵션의 알파벳]
"""
            
            # Generate questions using the model
            messages = [
                {"role": "system", 
                 "content": "You are EXAONE model from LG AI Research, a helpful Korean language assistant."},
                {"role": "user", "content": prompt}
            ]
            
            input_ids = tokenizer.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                return_tensors="pt"
            )
            
            # Check if CUDA is available, otherwise use CPU
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Generate text
            output = model.generate(
                input_ids.to(device),
                eos_token_id=tokenizer.eos_token_id,
                max_new_tokens=1024,
                do_sample=False,
            )
            
            result = tokenizer.decode(output[0])
        
        # Parse the generated questions
        questions = parse_generated_questions(result)
        
        # Cache the questions for future use
        if questions:
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(questions, f, ensure_ascii=False, indent=2)
                print(f"Cached {len(questions)} questions for future use.")
            except Exception as e:
                print(f"Error caching questions: {e}")
        
        return questions
        
    except Exception as e:
        print(f"Error generating questions with LLM: {e}")
        print("Falling back to basic question generation method.")
        return []

def parse_generated_questions(generated_text):
    """Parse the text generated by the LLM into structured question objects."""
    questions = []
    
    # Split by "SENTENCE:" to get individual questions
    question_blocks = generated_text.split("SENTENCE:")
    
    # Skip the first element which is the prompt
    for block in question_blocks[1:]:
        try:
            # Extract each component
            sentence_match = re.search(r'(.*?)QUESTION:', block, re.DOTALL)
            question_match = re.search(r'QUESTION:(.*?)OPTIONS:', block, re.DOTALL)
            options_match = re.search(r'OPTIONS:(.*?)CORRECT:', block, re.DOTALL)
            correct_match = re.search(r'CORRECT:\s*([A-D])', block, re.DOTALL)
            
            if sentence_match and question_match and options_match and correct_match:
                sentence = sentence_match.group(1).strip()
                question_text = question_match.group(1).strip()
                options_text = options_match.group(1).strip()
                correct_option = correct_match.group(1).strip()
                
                # Parse options
                options = []
                option_lines = options_text.split('\n')
                for line in option_lines:
                    if re.match(r'^[A-D]\.\s', line):
                        option_text = line[3:].strip()  # Remove "A. " prefix
                        options.append(option_text)
                
                if len(options) == 4:  # Ensure we have all 4 options
                    questions.append({
                        'sentence': sentence,
                        'question_text': question_text,
                        'options': options,
                        'correct_option': correct_option
                    })
        except Exception as e:
            print(f"Error parsing a question: {e}")
            continue
    
    return questions

def check_model_availability(model_key):
    """Check if a specific model is available."""
    try:
        model_info = MODELS.get(model_key)
        if not model_info:
            return False
            
        model_name = model_info["name"]
        
        if model_key == "gpt2":
            # Just check if we can initialize the pipeline
            try:
                _ = pipeline('text-classification', 
                             model='distilbert-base-uncased',
                             cache_dir=MODEL_CACHE_DIR)
                return True
            except:
                return False
                
        elif model_key == "exaone":
            try:
                # Just check if we can initialize the tokenizer
                _ = AutoTokenizer.from_pretrained(model_name, cache_dir=MODEL_CACHE_DIR)
                return True
            except:
                return False
                
        return False
    except:
        return False

def use_llm_for_questions():
    """Check which LLMs are available for generating questions."""
    available_models = {}
    
    try:
        import torch
        
        # Check if CUDA is available (for better performance)
        has_cuda = torch.cuda.is_available()
        print(f"CUDA availability: {'Yes' if has_cuda else 'No'}")
        
        # Check GPT-2 availability
        gpt2_available = check_model_availability("gpt2")
        if gpt2_available:
            available_models["gpt2"] = MODELS["gpt2"]
            
        # Check EXAONE availability
        exaone_available = check_model_availability("exaone")
        if exaone_available:
            available_models["exaone"] = MODELS["exaone"]
            
        if available_models:
            print(f"Found {len(available_models)} available LLM models for question generation.")
            return available_models
        else:
            print("No LLM models available.")
            return {}
            
    except ImportError as e:
        print(f"Required libraries not available: {e}")
        print("Please install the required packages with: pip install -r requirements.txt")
        return {}

def display_topik_question(question, question_num, total_questions):
    """Display a TOPIK-style question to the user."""
    clear_screen()
    print(f"\n🎧 TOPIK Question {question_num} of {total_questions}\n")
    print(f"Listen to the following sentence:")
    print(f"\n{question['sentence']}\n")
    
    print("Question:")
    print(question['question_text'])
    print()
    
    # Display options
    for i, option in enumerate(question['options']):
        print(f"{chr(65 + i)}. {option}")
    
    print("\nPress 'R' to replay the audio.")

def quiz_user_topik_style(questions, session_dir=None):
    """Quiz the user with TOPIK-style questions generated by the LLM."""
    score = 0
    total = len(questions)
    
    for i, question in enumerate(questions):
        display_topik_question(question, i+1, total)
        
        # Determine audio path
        audio_path = None
        if session_dir and "audio_path" in question and question["audio_path"]:
            audio_path = os.path.join(session_dir, question["audio_path"])
            if not os.path.exists(audio_path):
                audio_path = None
        
        # Play the audio for the sentence
        if audio_path and os.path.exists(audio_path):
            # Play existing audio file
            pygame.mixer.init()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.quit()
        else:
            # Generate new audio
            text_to_speech(question['sentence'])
        
        while True:
            user_input = input("\nYour answer (A/B/C/D or R to replay): ").upper()
            
            if user_input == 'R':
                if audio_path and os.path.exists(audio_path):
                    pygame.mixer.init()
                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                    pygame.mixer.quit()
                else:
                    text_to_speech(question['sentence'])
                continue
                
            if user_input in ['A', 'B', 'C', 'D']:
                break
                
            print("Invalid input. Please enter A, B, C, D, or R.")
        
        if user_input == question['correct_option']:
            print("\n✅ Correct!")
            score += 1
        else:
            print(f"\n❌ Incorrect. The correct answer was {question['correct_option']}")
        
        input("\nPress Enter to continue...")
    
    return score, total

def create_topik_quiz_session_dict(video_id, transcript, questions):
    """Create a dictionary of the TOPIK-style quiz session data for storing in JSON."""
    session = {
        "video_id": video_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "transcript": transcript,
        "quiz_type": "topik",
        "questions": []
    }
    
    for q in questions:
        question_data = {
            "sentence": q["sentence"],
            "question_text": q["question_text"],
            "options": q["options"],
            "correct_option": q["correct_option"],
            "audio_path": ""  # Will be filled later
        }
        session["questions"].append(question_data)
    
    return session

def main():
    """Main function to run the Korean Listening Comprehension app."""
    # Create directory for storing quiz sessions and model cache
    quiz_sessions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quiz_sessions")
    os.makedirs(quiz_sessions_dir, exist_ok=True)
    
    # Display app header with version
    clear_screen()
    print("=== 🇰🇷 Korean Listening Comprehension App v1.2 ===\n")
    print("Data and model files will be stored in:")
    print(f"- Model cache: {MODEL_CACHE_DIR}")
    print(f"- Question cache: {QUESTION_CACHE_DIR}")
    print(f"- Quiz sessions: {quiz_sessions_dir}\n")
    
    # Check which LLMs are available
    available_models = use_llm_for_questions()
    
    while True:
        print("\nOptions:")
        print("1. Start a new basic quiz")
        if available_models:
            print("2. Start a new TOPIK-style quiz (using LLM)")
        print("3. Load a saved quiz")
        print("4. Exit")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "4":
            print("\nThank you for using the Korean Listening Comprehension App. Goodbye!")
            break
            
        elif choice == "3":
            saved_sessions = []
            try:
                for root, dirs, files in os.walk(quiz_sessions_dir):
                    for file in files:
                        if file == "session_data.json":
                            saved_sessions.append(os.path.join(root, file))
            except Exception as e:
                print(f"Error finding saved sessions: {e}")
            
            if not saved_sessions:
                print("No saved quiz sessions found.")
                continue
                
            print("\nSaved quiz sessions:")
            for i, session_path in enumerate(saved_sessions):
                try:
                    with open(session_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        video_id = data.get('video_id', 'Unknown')
                        timestamp = data.get('timestamp', 'Unknown')
                        questions_count = len(data.get('questions', []))
                        quiz_type = data.get('quiz_type', 'basic')
                        print(f"{i+1}. Video: {video_id} - Date: {timestamp} - Questions: {questions_count} - Type: {quiz_type}")
                except:
                    print(f"{i+1}. [Could not read session data]")
            
            session_choice = input("\nEnter session number to load (or 0 to go back): ")
            try:
                session_index = int(session_choice) - 1
                if session_index == -1:
                    continue
                if 0 <= session_index < len(saved_sessions):
                    session_data = load_quiz_session(saved_sessions[session_index])
                    if session_data:
                        session_dir = os.path.dirname(saved_sessions[session_index])
                        questions = session_data.get('questions', [])
                        if questions:
                            quiz_type = session_data.get('quiz_type', 'basic')
                            if quiz_type == 'topik':
                                score, total = quiz_user_topik_style(questions, session_dir)
                            else:
                                score, total = quiz_user(questions, session_dir)
                            display_final_score(score, total)
                        else:
                            print("No questions found in this session.")
                else:
                    print("Invalid session number.")
            except ValueError:
                print("Please enter a valid number.")
        
        elif choice == "2" and available_models:
            print("\nAvailable models for TOPIK-style question generation:")
            model_keys = list(available_models.keys())
            
            for i, model_key in enumerate(model_keys):
                model = available_models[model_key]
                print(f"{i+1}. {model['display_name']}")
                print(f"   - {model['description']}")
                print(f"   - Size: {model['size']}")
                print(f"   - Korean support: {model['korean_support']}")
            
            model_choice = input("\nSelect model (number) or type 'back' to return: ")
            
            if model_choice.lower() == 'back':
                continue
                
            try:
                model_index = int(model_choice) - 1
                if 0 <= model_index < len(model_keys):
                    selected_model_key = model_keys[model_index]
                    selected_model = available_models[selected_model_key]
                    print(f"\nSelected model: {selected_model['display_name']}")
                else:
                    print("Invalid selection. Please try again.")
                    continue
            except ValueError:
                print("Please enter a valid number.")
                continue
            
            url = input("\nEnter a YouTube URL (or type 'back' to go back): ")
            
            if url.lower() == 'back':
                continue
                
            video_id = extract_youtube_id(url)
            if not video_id:
                print("Invalid YouTube URL. Please try again.")
                continue
                
            print("\nFetching Korean transcript...")
            
            transcript = fetch_korean_transcript(video_id)
            if not transcript:
                print("Please try another video with Korean subtitles.")
                continue
                
            print("Transcript fetched successfully!")
            print(f"Found transcript with {len(transcript.split())} words.")
            print(f"Generating TOPIK-style questions with {selected_model['display_name']} (this may take a moment)...")
            
            questions = generate_topik_questions_with_llm(transcript, num_questions=3, model_choice=selected_model_key)
            if not questions or len(questions) < 2:
                print("Could not generate enough questions. Please try another video or use the basic quiz option.")
                continue
            
            print(f"Generated {len(questions)} TOPIK-style questions.")
            
            session_data = create_topik_quiz_session_dict(video_id, transcript, questions)
            session_data["model"] = selected_model_key
            json_path = save_quiz_session(session_data, quiz_sessions_dir)
            
            print(f"Quiz data saved to {json_path}")
            input("Press Enter to start the quiz...")
            
            session_data = load_quiz_session(json_path)
            session_dir = os.path.dirname(json_path)
            
            score, total = quiz_user_topik_style(session_data.get("questions", []), session_dir)
            
            display_final_score(score, total)
                
        elif choice == "1":
            url = input("\nEnter a YouTube URL (or type 'back' to go back): ")
            
            if url.lower() == 'back':
                continue
                
            video_id = extract_youtube_id(url)
            if not video_id:
                print("Invalid YouTube URL. Please try again.")
                continue
                
            print("\nFetching Korean transcript...")
            
            transcript = fetch_korean_transcript(video_id)
            if not transcript:
                print("Please try another video with Korean subtitles.")
                continue
                
            print("Transcript fetched successfully!")
            print(f"Found transcript with {len(transcript.split())} words.")
            print("Generating questions...")
            
            sentences = extract_sentences(transcript, num_sentences=5)
            if not sentences:
                print("Could not extract suitable sentences from this transcript. Please try another video.")
                continue
                
            questions = generate_questions(sentences)
            if len(questions) < 3:
                print("Not enough questions could be generated. Please try another video.")
                continue
                
            print(f"Generated {len(questions)} questions.")
            
            session_data = create_quiz_session_dict(video_id, transcript, questions)
            json_path = save_quiz_session(session_data, quiz_sessions_dir)
            
            print(f"Quiz data saved to {json_path}")
            input("Press Enter to start the quiz...")
            
            session_data = load_quiz_session(json_path)
            session_dir = os.path.dirname(json_path)
            
            score, total = quiz_user(session_data.get("questions", []), session_dir)
            
            display_final_score(score, total)
            
        else:
            print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    main()