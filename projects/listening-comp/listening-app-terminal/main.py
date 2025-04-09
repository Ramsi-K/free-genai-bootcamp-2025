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

# Import progress functions
from progress import update_progress, get_progress_stats, display_progress, display_final_score
# Import translation function from app.py
from app import translate_korean_to_english, generate_topik_questions_with_llm
# Import audio utilities
from audio_utils import play_audio_with_speed, text_to_speech_with_speed, save_audio_file, practice_pronunciation
# Import vocabulary functions
from vocabulary import save_vocabulary, browse_vocabulary, get_vocabulary_count
# Import config
from config import APP_CONFIG, MODELS

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
    
    # Simply set different parameters based on difficulty level
    if difficulty == "easy":
        min_length = 10
        max_length = 50
        num_sentences = 5
    elif difficulty == "hard":
        min_length = 30
        max_length = 100
        num_sentences = 8
    else:  # medium
        min_length = 20
        max_length = 80
        num_sentences = 6
    
    # Split the transcript by sentence endings
    sentences = re.split(r'[.!?]\s+', transcript)
    
    # Filter sentences by length according to difficulty
    valid_sentences = [s for s in sentences if min_length <= len(s) <= max_length]
    
    if not valid_sentences:
        # Fallback to more lenient filtering if we couldn't find sentences
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
                # Use the imported function from app.py with use_streamlit=False
                translation = translate_korean_to_english(question['sentence'], use_streamlit=False)
                print(f"\nTranslation: {translation}")
            except Exception as e:
                print(f"\nSorry, translation failed: {e}")
        
        input("\nPress Enter to continue...")
    
    # Save vocabulary using the imported function
    if vocabulary:
        save_vocabulary(vocabulary)
    
    return score, total

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
    """Save quiz session data without generating audio files."""
    # Create session directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    video_id = session_data["video_id"]
    session_dir = os.path.join(base_dir, f"{video_id}_{timestamp}")
    os.makedirs(session_dir, exist_ok=True)
    
    # Create audio directory - but don't generate audio yet
    audio_dir = os.path.join(session_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    # Just set placeholder paths for audio files
    for i, question in enumerate(session_data["questions"]):
        audio_filename = f"question_{i+1}.mp3"
        audio_path = os.path.join(audio_dir, audio_filename)
        
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
                english = translate_korean_to_english(korean, use_streamlit=False)
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

def display_question(question, current_num, total):
    """Display a question to the user in a clear format."""
    clear_screen()
    print(f"Question {current_num} of {total}\n")
    
    if "blank_sentence" in question:
        # Basic fill-in-the-blank format
        print(question["blank_sentence"])
    elif "question_text" in question:
        # TOPIK-style format
        print(question["question_text"])
    
    print("\nOptions:")
    options = question.get("options", [])
    option_letters = ["A", "B", "C", "D"]
    
    for i, option in enumerate(options):
        if i < len(option_letters):
            print(f"{option_letters[i]}. {option}")

def quiz_user_topik_style(questions, session_dir=None, audio_speed="normal"):
    """Quiz the user with TOPIK-style listening comprehension questions."""
    score = 0
    total = len(questions)
    vocabulary = []  # Track vocabulary
    
    for i, question in enumerate(questions):
        # First display the question
        display_question(question, i+1, total)
        
        # Add vocabulary from this question (e.g., the sentence)
        if "sentence" in question:
            vocabulary.append({
                "word": question["sentence"].split()[0] if question["sentence"].split() else "",
                "context": question["sentence"]
            })
        
        # Determine audio path
        audio_path = None
        if session_dir and "audio_path" in question and question["audio_path"]:
            audio_path = os.path.join(session_dir, question["audio_path"])
            
            # Check if audio exists, if not, generate it now
            if not os.path.exists(audio_path):
                # print(f"Generating audio for question {i+1}...")
                save_audio_file(question["sentence"], audio_path)
        
        # # Play the audio with selected speed
        # print("\nPlaying audio for this question...")
        # if audio_path and os.path.exists(audio_path):
        #     # Play existing audio file with speed control
        #     play_audio_with_speed(audio_path, audio_speed)
        # else:
        #     # Generate new audio with speed on the fly (don't save)
        #     text_to_speech_with_speed(question['sentence'], audio_speed)
        
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
            print("\n✅ Correct!")
            score += 1
        else:
            print(f"\n❌ Incorrect. The correct answer was {question['correct_option']}.")
        
        print("\nThe sentence was:")
        print(f"「{question['sentence']}」")
        
        # Ask if user wants to translate this sentence
        if input("\nWould you like an English translation? (y/n): ").lower() == 'y':
            try:
                translation = translate_korean_to_english(question['sentence'], use_streamlit=False)
                print(f"\nTranslation: {translation}")
            except Exception as e:
                print(f"\nSorry, translation failed: {e}")
        
        input("\nPress Enter to continue...")
    
    # Save vocabulary
    if vocabulary:
        save_vocabulary(vocabulary)
    
    return score, total

def create_topik_quiz_session_dict(video_id, transcript, questions, difficulty="medium", model="gpt2"):
    """Create a dictionary of TOPIK-style quiz session data for storing in JSON."""
    session = {
        "video_id": video_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "transcript": transcript,
        "quiz_type": "topik",
        "difficulty": difficulty,
        "model_used": model,
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
            browse_vocabulary()
                
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
            
            # print(f"Quiz data saved to {json_path}")
            
            # Select audio speed
            print("\nSelect audio speed:")
            print("1. Normal")
            print("2. Slow")
            speed_choice = input("Enter choice (1/2): ")
            audio_speed = "normal" if speed_choice != "2" else "slow"
            
            # Wait for user confirmation before starting quiz and playing audio
            input("\nPress Enter to start the quiz...")
            
            # Load the saved session to get the audio paths
            session_data = load_quiz_session(json_path)
            
            # Make sure session_data is properly loaded before proceeding
            if not session_data or not session_data.get("questions"):
                print("Error: Could not load saved session data. Please try again.")
                continue
                
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
            
            # print(f"Quiz data saved to {json_path}")
            
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