import os
import re
import random
import tempfile
import json
import datetime
import hashlib
import csv
import shutil
import wave
import pyaudio
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import time
import pygame
import torch
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from gtts import gTTS
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from translate import Translator

# Import progress functions
from progress import update_progress, get_progress_stats, display_progress

# Define directories
MODEL_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_cache")
QUESTION_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "question_cache")
VOCAB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocabulary")
RECORDINGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recordings")
EXPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
USER_STATS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_stats.json")

# Create directories
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
os.makedirs(QUESTION_CACHE_DIR, exist_ok=True)
os.makedirs(VOCAB_DIR, exist_ok=True)
os.makedirs(RECORDINGS_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

# App configuration
APP_CONFIG = {
    "version": "2.0",
    "difficulty_levels": {
        "easy": {
            "sentence_length_range": (10, 50),
            "num_questions": 3,
            "playback_speed": 0.8
        },
        "medium": {
            "sentence_length_range": (20, 80),
            "num_questions": 4,
            "playback_speed": 1.0
        },
        "hard": {
            "sentence_length_range": (30, 150),
            "num_questions": 5,
            "playback_speed": 1.0
        }
    },
    "default_difficulty": "medium",
    "audio_speeds": {
        "slow": 0.75,
        "normal": 1.0
    },
    "default_audio_speed": "normal"
}

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

def extract_sentences_by_difficulty(transcript, difficulty="medium"):
    """Extract sentences from the transcript based on difficulty level."""
    if not transcript:
        return []
    
    # Get difficulty settings
    difficulty_config = APP_CONFIG["difficulty_levels"].get(
        difficulty, APP_CONFIG["difficulty_levels"]["medium"])
    
    min_length, max_length = difficulty_config["sentence_length_range"]
    num_sentences = difficulty_config["num_questions"]
    
    # Split the transcript by sentence endings
    sentences = re.split(r'[.!?]\s+', transcript)
    
    # Filter sentences by length according to difficulty
    valid_sentences = [s for s in sentences if min_length <= len(s) <= max_length]
    
    if not valid_sentences:
        # Fallback to medium difficulty if needed
        medium_config = APP_CONFIG["difficulty_levels"]["medium"]
        min_length, max_length = medium_config["sentence_length_range"]
        valid_sentences = [s for s in sentences if min_length <= len(s) <= max_length]
        
        if not valid_sentences:
            # Last resort: just take whatever sentences we have
            valid_sentences = [s for s in sentences if len(s) >= 10]
    
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
                             )
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

def play_audio_with_speed(file_path, speed="normal"):
    """Play audio with speed control using pygame."""
    try:
        # Initialize pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        
        # Set playback speed - only available in newer pygame versions
        # If not available, warn user but continue with normal speed
        try:
            target_speed = APP_CONFIG["audio_speeds"].get(speed, 1.0)
            if hasattr(pygame.mixer.music, 'set_pos'):
                pygame.mixer.music.set_pos(target_speed)
        except:
            if speed != "normal":
                print(f"Note: Speed control ({speed}) not available with this version of pygame.")
        
        # Play and wait for completion
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
    except Exception as e:
        print(f"Error playing audio: {e}")
    finally:
        pygame.mixer.quit()

def text_to_speech_with_speed(text, speed="normal", save_path=None):
    """Generate Korean text-to-speech audio with speed control and play it."""
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
    temp_filename = temp_file.name
    temp_file.close()
    
    try:
        # Generate TTS - for gTTS, "slow" is a separate parameter
        is_slow = False
        if speed == "slow":
            is_slow = True
            
        tts = gTTS(text=text, lang='ko', slow=is_slow)
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
        
        # Play the audio with speed control
        play_audio_with_speed(temp_filename, speed)
        
        return temp_filename if not save_path else save_path
    
    finally:
        # Cleanup temporary file if we're not saving it
        if os.path.exists(temp_filename) and save_path:
            os.unlink(temp_filename)

def save_audio_file(text, filename):
    """Generate Korean text-to-speech audio and save to a file."""
    try:
        tts = gTTS(text=text, lang='ko', slow=False)
        tts.save(filename)
        return True
    except Exception as e:
        print(f"Error saving audio: {e}")
        return False

def display_question(question, question_num, total_questions):
    """Display a question to the user."""
    clear_screen()
    print(f"\n🎧 Question {question_num} of {total_questions}\n")
    print(f"Listen to the following sentence:")
    print(f"\n{question['blank_sentence']}\n")
    
    # Display options
    for i, option in enumerate(question['options']):
        print(f"{chr(65 + i)}. {option}")
    
    print("\nPress 'R' to replay the audio, 'S' to switch speed, 'P' to practice pronunciation.")

def quiz_user_with_options(questions, session_dir=None, audio_speed="normal"):
    """Quiz the user with speed control and more options."""
    score = 0
    total = len(questions)
    vocabulary = []  # Track vocabulary
    
    for i, question in enumerate(questions):
        display_question(question, i+1, total)
        
        # Add vocabulary from this question
        if "removed_word" in question:
            vocabulary.append({
                "word": question["removed_word"],
                "context": question["sentence"]
            })
        
        # Determine audio path
        audio_path = None
        if session_dir and "audio_path" in question and question["audio_path"]:
            audio_path = os.path.join(session_dir, question["audio_path"])
            if not os.path.exists(audio_path):
                audio_path = None
        
        # Play the audio with selected speed
        if audio_path and os.path.exists(audio_path):
            # Play existing audio file with speed control
            play_audio_with_speed(audio_path, audio_speed)
        else:
            # Generate new audio with speed
            text_to_speech_with_speed(question['sentence'], audio_speed)
        
        while True:
            user_input = input("\nYour answer (A/B/C/D), R to replay, S to switch speed, P to practice pronunciation: ").upper()
            
            if user_input == 'R':
                # Replay with current speed
                if audio_path and os.path.exists(audio_path):
                    play_audio_with_speed(audio_path, audio_speed)
                else:
                    text_to_speech_with_speed(question['sentence'], audio_speed)
                continue
                
            elif user_input == 'S':
                # Toggle speed between normal and slow
                audio_speed = "slow" if audio_speed == "normal" else "normal"
                print(f"\nSwitched to {audio_speed} speed.")
                if audio_path and os.path.exists(audio_path):
                    play_audio_with_speed(audio_path, audio_speed)
                else:
                    text_to_speech_with_speed(question['sentence'], audio_speed)
                continue
                
            elif user_input == 'P':
                # Practice pronunciation
                practice_pronunciation(question['sentence'])
                continue
                
            elif user_input in ['A', 'B', 'C', 'D']:
                break
                
            else:
                print("Invalid input. Please enter A, B, C, D, R, S, or P.")
        
        if user_input == question['correct_option']:
            print("\n✅ Correct! The answer was: " + question.get('removed_word', ''))
            score += 1
        else:
            correct_word = question.get('removed_word', question.get('correct_option', ''))
            print(f"\n❌ Incorrect. The correct answer was {question['correct_option']}: {correct_word}")
        
        print("\nOriginal sentence:")
        print(f"{question['sentence']}")
        
        # Ask if user wants to translate this sentence
        if input("\nWould you like an English translation? (y/n): ").lower() == 'y':
            try:
                translation = translate_korean_to_english(question['sentence'])
                print(f"\nTranslation: {translation}")
            except:
                print("\nSorry, translation service is not available.")
        
        input("\nPress Enter to continue...")
    
    # Save vocabulary
    if vocabulary:
        save_vocabulary(vocabulary)
    
    return score, total

def practice_pronunciation(korean_text):
    """Let user record their pronunciation of Korean text and get feedback."""
    print("\n🎤 Pronunciation Practice")
    print("\nListen to the correct pronunciation first:")
    text_to_speech_with_speed(korean_text, "normal")
    
    # Recording settings
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 5
    
    # Create a unique filename for this recording
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    recording_path = os.path.join(RECORDINGS_DIR, f"pronunciation_{timestamp}.wav")
    
    # Prepare for recording
    input("\nPress Enter when ready to record your pronunciation (5 seconds)...")
    
    try:
        # Start recording
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
        
        print("\nRecording... speak now")
        frames = []
        
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        print("Recording finished")
        
        # Stop recording
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Save the recording
        with wave.open(recording_path, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        
        print(f"\nYour pronunciation has been saved to {recording_path}")
        
        # Simple feedback (in reality this would use speech recognition)
        print("\nWould you like to hear your pronunciation?")
        if input("(y/n): ").lower() == 'y':
            play_audio_with_speed(recording_path, "normal")
            
        print("\nWould you like to hear the correct pronunciation again for comparison?")
        if input("(y/n): ").lower() == 'y':
            text_to_speech_with_speed(korean_text, "normal")
            
        return True
        
    except Exception as e:
        print(f"Error during pronunciation practice: {e}")
        return False

def translate_korean_to_english(korean_text):
    """Translate Korean text to English using a simple approach."""
    # This would ideally use a translation API
    # but for now we'll return a placeholder message
    translator= Translator(to_lang="en")
    translation = translator.translate(korean_text)
    return translation

def save_vocabulary(vocabulary_items):
    """Save vocabulary items to a file for later review."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    vocab_file = os.path.join(VOCAB_DIR, f"vocabulary_{timestamp}.json")
    
    try:
        with open(vocab_file, 'w', encoding='utf-8') as f:
            json.dump(vocabulary_items, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving vocabulary: {e}")
        return False

def create_quiz_session_dict(video_id, transcript, questions):
    """Create a dictionary of the quiz session data for storing in JSON."""
    session = {
        "video_id": video_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "transcript": transcript,
        "quiz_type": "basic",
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

def export_to_anki(session_data, export_file=None):
    """Export session data to Anki-compatible CSV format."""
    if not export_file:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = os.path.join(EXPORTS_DIR, f"anki_export_{timestamp}.csv")
    
    try:
        with open(export_file, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            
            # Write header
            writer.writerow(['Korean', 'English', 'Audio', 'Tags'])
            
            # Write questions
            for question in session_data.get('questions', []):
                korean = question.get('sentence', '')
                
                # For Anki sound field format
                audio = ''
                if 'audio_path' in question and question['audio_path']:
                    audio_filename = os.path.basename(question['audio_path'])
                    audio = f'[sound:{audio_filename}]'
                
                # Get any additional fields
                english = translate_korean_to_english(korean)
                tags = "korean listening practice"
                
                writer.writerow([korean, english, audio, tags])
                
            # Copy audio files if needed
            session_dir = os.path.dirname(export_file)
            audio_dir = os.path.join(session_dir, "audio")
            os.makedirs(audio_dir, exist_ok=True)
            
            for question in session_data.get('questions', []):
                if 'audio_path' in question and question['audio_path']:
                    src_path = os.path.join(os.path.dirname(session_data.get('_session_path', '')), 
                                           question['audio_path'])
                    if os.path.exists(src_path):
                        dst_path = os.path.join(audio_dir, os.path.basename(question['audio_path']))
                        shutil.copy2(src_path, dst_path)
        
        print(f"\nExported to Anki format: {export_file}")
        print("Note: To use this in Anki, import the CSV file and copy any audio files to your Anki media folder.")
        
        return export_file
        
    except Exception as e:
        print(f"Error exporting to Anki format: {e}")
        return None

def main():
    """Main function to run the Korean Listening Comprehension app."""
    # Create directories
    quiz_sessions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quiz_sessions")
    os.makedirs(quiz_sessions_dir, exist_ok=True)
    
    # Load user stats - Use progress.py instead of local function
    user_stats = get_progress_stats() or {}
    
    # Check which LLMs are available
    available_models = use_llm_for_questions()
    
    # Display app header with version
    clear_screen()
    print("=== 🇰🇷 Korean Listening Comprehension App v2.0 ===\n")
    
    # Check if there are any previous sessions
    has_previous_sessions = False
    try:
        for root, dirs, files in os.walk(quiz_sessions_dir):
            for file in files:
                if file == "session_data.json":
                    has_previous_sessions = True
                    break
            if has_previous_sessions:
                break
    except:
        pass
    
    while True:
        print("\nMain Menu:")
        print("1. Basic Quiz (Fill-in-the-blank)")
        if available_models:
            print("2. TOPIK-style Quiz (Listening comprehension)")
        if has_previous_sessions:
            print("3. Load a saved quiz")
        print("4. View your learning progress")
        print("5. Browse vocabulary")
        print("6. Export to Anki")
        print("7. Exit")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "7":
            print("\nThank you for using the Korean Listening Comprehension App. Goodbye!")
            break
            
        elif choice == "4":
            # View learning progress - Use progress.py function
            display_progress()
            
        elif choice == "5":
            # Browse vocabulary
            vocab_files = [f for f in os.listdir(VOCAB_DIR) if f.endswith('.json')]
            
            if not vocab_files:
                print("No vocabulary files found yet. Complete some quizzes to build your vocabulary.")
                input("\nPress Enter to continue...")
                continue
                
            print("\nAvailable vocabulary lists:")
            for i, vfile in enumerate(vocab_files):
                print(f"{i+1}. {vfile}")
                
            vfile_choice = input("\nEnter number to view (or 0 to go back): ")
            try:
                vfile_index = int(vfile_choice) - 1
                if vfile_index == -1:
                    continue
                if 0 <= vfile_index < len(vocab_files):
                    with open(os.path.join(VOCAB_DIR, vocab_files[vfile_index]), 'r', encoding='utf-8') as f:
                        vocab_list = json.load(f)
                        
                    clear_screen()
                    print(f"\n=== Vocabulary List ({vocab_files[vfile_index]}) ===\n")
                    for i, item in enumerate(vocab_list):
                        print(f"{i+1}. {item['word']} - Context: {item['context']}")
                        
                    input("\nPress Enter to continue...")
            except:
                print("Invalid selection.")
                
        elif choice == "6":
            # Export to Anki
            if not has_previous_sessions:
                print("No quiz sessions available to export. Complete a quiz first.")
                continue
                
            # Select a session to export
            saved_sessions = []
            try:
                for root, dirs, files in os.walk(quiz_sessions_dir):
                    for file in files:
                        if file == "session_data.json":
                            saved_sessions.append(os.path.join(root, file))
            except Exception as e:
                print(f"Error finding saved sessions: {e}")
            
            print("\nSelect a session to export to Anki:")
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
            
            session_choice = input("\nEnter session number (or 0 to go back): ")
            try:
                session_index = int(session_choice) - 1
                if session_index == -1:
                    continue
                if 0 <= session_index < len(saved_sessions):
                    session_data = load_quiz_session(saved_sessions[session_index])
                    if session_data:
                        # Add the session path to the data for reference when copying audio files
                        session_data["_session_path"] = saved_sessions[session_index]
                        export_file = export_to_anki(session_data)
                        if export_file:
                            print(f"Successfully exported to {export_file}")
                        input("\nPress Enter to continue...")
                else:
                    print("Invalid session number.")
            except ValueError:
                print("Please enter a valid number.")
            
        elif choice == "3" and has_previous_sessions:
            # Load and play a saved quiz
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
                            # Select audio speed
                            print("\nSelect audio speed:")
                            print("1. Normal")
                            print("2. Slow")
                            speed_choice = input("Enter choice (1/2): ")
                            audio_speed = "normal" if speed_choice != "2" else "slow"
                            
                            # Run the appropriate quiz based on type
                            quiz_type = session_data.get('quiz_type', 'basic')
                            if quiz_type == 'topik':
                                score, total = quiz_user_topik_style(questions, session_dir, audio_speed)
                            else:
                                score, total = quiz_user_with_options(questions, session_dir, audio_speed)
                                
                            display_final_score(score, total)
                            
                            # Update user statistics using progress.py
                            quiz_stats = {
                                "difficulty": session_data.get("difficulty", "medium"),
                                "total_questions": total,
                                "correct_answers": score,
                                "accuracy": round((score / total) * 100) if total > 0 else 0
                            }
                            update_progress(quiz_stats)
                        else:
                            print("No questions found in this session.")
                else:
                    print("Invalid session number.")
            except ValueError:
                print("Please enter a valid number.")
        
        elif choice == "2" and available_models:
            # Start a new TOPIK-style quiz with LLM
            
            # Model selection for TOPIK-style quiz
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
            
            # Get YouTube URL
            url = input("\nEnter a YouTube URL (or type 'back' to go back): ")
            
            if url.lower() == 'back':
                continue
                
            # Extract video ID
            video_id = extract_youtube_id(url)
            if not video_id:
                print("Invalid YouTube URL. Please try again.")
                continue
                
            print("\nFetching Korean transcript...")
            
            # Fetch Korean transcript
            transcript = fetch_korean_transcript(video_id)
            if not transcript:
                print("Please try another video with Korean subtitles.")
                continue
                
            print("Transcript fetched successfully!")
            print(f"Found transcript with {len(transcript.split())} words.")
            
            # Select difficulty
            print("\nSelect difficulty level for TOPIK-style questions:")
            print("1. Easy (simpler questions)")
            print("2. Medium (standard TOPIK-style)")
            print("3. Hard (advanced vocabulary and questions)")
            
            diff_choice = input("Enter choice (1/2/3): ")
            difficulty = "easy" if diff_choice == "1" else "hard" if diff_choice == "3" else "medium"
            
            print(f"\nSelected difficulty: {difficulty}")
            print(f"Generating TOPIK-style questions with {selected_model['display_name']} (this may take a while)...")
            
            # Generate questions using selected LLM
            questions = generate_topik_questions_with_llm(transcript, num_questions=3, 
                                               model_choice=selected_model_key,
                                               difficulty=difficulty)
            
            if not questions or len(questions) < 2:
                print("Could not generate enough questions. Please try another video.")
                continue
            
            print(f"Generated {len(questions)} TOPIK-style questions.")
            
            # Create and save quiz session data with model info
            session_data = create_topik_quiz_session_dict(video_id, transcript, questions, 
                                             difficulty=difficulty, model=selected_model_key)
            
            json_path = save_quiz_session(session_data, quiz_sessions_dir)
            
            print(f"Quiz data saved to {json_path}")
            
            # Select audio speed
            print("\nSelect audio speed:")
            print("1. Normal")
            print("2. Slow")
            speed_choice = input("Enter choice (1/2): ")
            audio_speed = "normal" if speed_choice != "2" else "slow"
            
            input("Press Enter to start the quiz...")
            
            # Load the saved session to get the audio paths
            session_data = load_quiz_session(json_path)
            session_dir = os.path.dirname(json_path)
            
            # Quiz the user with TOPIK-style questions
            score, total = quiz_user_topik_style(session_data.get("questions", []), session_dir, audio_speed)
            
            # Display final score
            display_final_score(score, total)
            
            # Update user statistics using progress.py
            quiz_stats = {
                "difficulty": session_data.get("difficulty", "medium"),
                "total_questions": total,
                "correct_answers": score,
                "accuracy": round((score / total) * 100) if total > 0 else 0
            }
            update_progress(quiz_stats)
            
            # Mark that we have sessions
            has_previous_sessions = True
        
        elif choice == "1":
            # Start a new basic fill-in-the-blank quiz
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
            
            # Select difficulty
            print("\nSelect difficulty level:")
            print("1. Easy (shorter sentences, slower playback)")
            print("2. Medium (standard)")
            print("3. Hard (longer sentences, more questions)")
            
            diff_choice = input("Enter choice (1/2/3): ")
            difficulty = "easy" if diff_choice == "1" else "hard" if diff_choice == "3" else "medium"
            
            print(f"\nSelected difficulty: {difficulty}")
            sentences = extract_sentences_by_difficulty(transcript, difficulty)
            
            if not sentences:
                print("Could not extract suitable sentences from this transcript. Please try another video.")
                continue
                
            questions = generate_questions(sentences)
            if len(questions) < 2:  # Allow as few as 2 questions
                print("Not enough questions could be generated. Please try another video.")
                continue
                
            print(f"Generated {len(questions)} questions.")
            
            # Create and save session
            session_data = create_quiz_session_dict(video_id, transcript, questions)
            session_data["difficulty"] = difficulty
            json_path = save_quiz_session(session_data, quiz_sessions_dir)
            
            print(f"Quiz data saved to {json_path}")
            
            # Select audio speed
            print("\nSelect audio speed:")
            print("1. Normal")
            print("2. Slow")
            speed_choice = input("Enter choice (1/2): ")
            audio_speed = "normal" if speed_choice != "2" else "slow"
            
            input("\nPress Enter to start the quiz...")
            
            # Load the saved session to get the audio paths
            session_data = load_quiz_session(json_path)
            session_dir = os.path.dirname(json_path)
            
            # Run the quiz with selected options
            score, total = quiz_user_with_options(session_data.get("questions", []), session_dir, audio_speed)
            
            # Display final score
            display_final_score(score, total)
            
            # Update user statistics using progress.py
            quiz_stats = {
                "difficulty": session_data.get("difficulty", "medium"),
                "total_questions": total,
                "correct_answers": score,
                "accuracy": round((score / total) * 100) if total > 0 else 0
            }
            update_progress(quiz_stats)
            
            # Mark that we have sessions
            has_previous_sessions = True

if __name__ == "__main__":
    main()