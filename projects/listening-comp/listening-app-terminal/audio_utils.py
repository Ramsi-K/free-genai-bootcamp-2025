import os
import wave
import librosa
import numpy as np
import soundfile as sf
import tempfile
import hashlib
import pyaudio
import time
import datetime
import json
from gtts import gTTS
from config import APP_CONFIG
import pygame

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Define paths for storing recordings - use app directory for better reliability
APP_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDINGS_DIR = os.path.join(APP_DIR, "recordings")
USER_RECORDINGS_DIR = os.path.join(RECORDINGS_DIR, "user_recordings")
SYSTEM_RECORDINGS_DIR = os.path.join(RECORDINGS_DIR, "system_recordings")
TEMP_DIR = os.path.join(APP_DIR, "temp_audio")  # Local temp directory without spaces

# Create necessary directories
os.makedirs(USER_RECORDINGS_DIR, exist_ok=True)
os.makedirs(SYSTEM_RECORDINGS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

def play_audio(file_path, block=True):
    """Play audio using pygame (more reliable than playsound)."""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Audio file does not exist: {file_path}")
            return False
        
        # Use absolute path to avoid any path issues
        abs_path = os.path.abspath(file_path)
        
        # Initialize pygame mixer if needed
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Load and play the audio file
        # print(f"Playing audio: {os.path.basename(abs_path)}")
        pygame.mixer.music.load(abs_path)
        pygame.mixer.music.play()
        
        # Wait for playback to finish if blocking
        if block:
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
        return True
    
    except Exception as e:
        print(f"Error playing audio: {e}")
        return False

def play_audio_with_speed(file_path, speed="normal"):
    """Play an audio file with speed control."""
    try:
        # Check if file exists first
        if not os.path.exists(file_path):
            print(f"Audio file does not exist: {file_path}")
            return False
            
        # Define default speed factors
        speed_factors = {
            "slow": 0.75,
            "normal": 1.0,
            "fast": 1.25
        }
        
        # Use config if available, otherwise use defaults
        try:
            if "audio_speeds" in APP_CONFIG:
                speed_factor = APP_CONFIG["audio_speeds"].get(speed, 1.0)
            else:
                speed_factor = speed_factors.get(speed, 1.0)
        except:
            speed_factor = speed_factors.get(speed, 1.0)
        
        # If normal speed, just play directly
        if speed_factor == 1.0:
            return play_audio(file_path)
            
        # For adjusted speeds, create temporary file with adjusted speed
        # Load audio file
        y, sr = librosa.load(file_path, sr=None)
        
        # Apply speed modification
        if speed_factor > 0:  # Make sure we don't divide by zero
            y_stretched = librosa.effects.time_stretch(y=y, rate=speed_factor)
            
            # Create a temporary file for the speed-adjusted audio in our local temp dir
            temp_filename = f"speed_{int(time.time())}_{abs(hash(file_path))}.wav"
            temp_filepath = os.path.join(TEMP_DIR, temp_filename)
            sf.write(temp_filepath, y_stretched, sr)
            
            # Play the temporary file
            result = play_audio(temp_filepath)
            
            # Clean up
            try:
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
            except:
                pass  # It's ok if cleanup fails
                
            return result
        else:
            return play_audio(file_path)
            
    except Exception as e:
        print(f"Error playing audio with speed control: {e}")
        return False

def text_to_speech_with_speed(text, speed="normal", save_path=None):
    """Generate and play TTS with speed control. Optionally save to a specific path."""
    try:
        # If no save path specified, save to system recordings directory with unique name
        if not save_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            filename = f"tts_{timestamp}_{text_hash}.mp3"
            save_path = os.path.join(SYSTEM_RECORDINGS_DIR, filename)
        
        # Ensure the path has no spaces or problematic characters
        save_path = os.path.abspath(save_path)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Generate TTS
        # print(f"Generating TTS audio for: {text[:50]}..." if len(text) > 50 else f"Generating TTS audio for: {text}")
        is_slow = speed == "slow"  # gTTS has a built-in slow option
        tts = gTTS(text=text, lang='ko', slow=is_slow)
        tts.save(save_path)
        
        # Verify the file was created
        if not os.path.exists(save_path):
            print(f"Failed to create audio file at: {save_path}")
            return None
            
        # print(f"Audio saved to: {save_path}")
        
        # Play the audio with speed control
        print("Playing audio...")
        play_audio_with_speed(save_path, speed)
        
        return save_path
        
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        return None

def save_audio_file(text, filename):
    """Generate Korean text-to-speech audio and save to a file."""
    try:
        return text_to_speech_with_speed(text, "normal", save_path=filename)
    except Exception as e:
        print(f"Error saving audio: {e}")
        return None

def compare_audio(user_path, reference_path):
    """Compare user's pronunciation with reference audio using MFCC and DTW."""
    try:
        # print(f"Comparing audio files:\n- User: {user_path}\n- Reference: {reference_path}")
        
        # Check if files exist
        if not os.path.exists(user_path):
            print(f"User audio file does not exist: {user_path}")
            return None
        if not os.path.exists(reference_path):
            print(f"Reference audio file does not exist: {reference_path}")
            return None
            
        # Load both audio files
        y1, sr1 = librosa.load(user_path, sr=None)
        y2, sr2 = librosa.load(reference_path, sr=None)

        # Resample if needed
        if sr1 != sr2:
            y2 = librosa.resample(y=y2, orig_sr=sr2, target_sr=sr1)
            sr2 = sr1

        # Extract MFCC features with proper dimensions
        mfcc1 = librosa.feature.mfcc(y=y1, sr=sr1, n_mfcc=13)
        mfcc2 = librosa.feature.mfcc(y=y2, sr=sr2, n_mfcc=13)
        
        # Print shapes for debugging
        print(f"MFCC shapes: User={mfcc1.shape}, Reference={mfcc2.shape}")
        
        # Handle empty or very short audio
        if mfcc1.shape[1] < 2 or mfcc2.shape[1] < 2:
            print(f"Audio too short. Shapes: {mfcc1.shape}, {mfcc2.shape}")
            return 45.0  # Return a mediocre score for very short audio
            
        # Use Dynamic Time Warping to compare the audio features
        D, wp = librosa.sequence.dtw(X=mfcc1, Y=mfcc2, metric='cosine')

        # Get final cost
        raw_score = D[-1, -1]
        print(f"Raw DTW score: {raw_score}")

        # FIXED: Improved normalization for DTW scores
        # Lower DTW scores are better (0 would be perfect match)
        # Typical range for Korean speech might be 5-50
        # Normalize to 0-100 with more reasonable scaling
        if raw_score < 5:  # Excellent match
            similarity_score = 95.0
        elif raw_score > 50:  # Very poor match
            similarity_score = max(10.0, 100 - raw_score)
        else:
            # Map 5-50 range to 95-10 range (inverse relationship)
            similarity_score = 95.0 - ((raw_score - 5) * (95.0 - 10.0) / (50.0 - 5.0))
        
        return round(similarity_score, 1)
    
    except Exception as e:
        print(f"[❌] Audio comparison failed: {e}")
        # Return a default mediocre score when comparison fails
        return 50.0

def practice_pronunciation(text):
    """Record user's pronunciation and compare with the correct pronunciation."""
    try:
        print("\n🎤 Pronunciation Practice")
        print(f"Original text: {text}")
        
        # Generate unique filenames based on text content and timestamp
        text_hash = hashlib.md5(text.encode()).hexdigest()[:12]
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create paths for reference and user recordings
        reference_filename = f"reference_{text_hash}.wav"
        reference_file = os.path.join(SYSTEM_RECORDINGS_DIR, reference_filename)
        
        user_filename = f"user_{timestamp}_{text_hash}.wav"
        user_file = os.path.join(USER_RECORDINGS_DIR, user_filename)
        
        # First play the correct pronunciation
        print("\nListen to the correct pronunciation...")
        
        # Generate reference audio if it doesn't exist
        if not os.path.exists(reference_file):
            # First create mp3 with gTTS
            temp_mp3 = os.path.join(SYSTEM_RECORDINGS_DIR, f"temp_{text_hash}.mp3")
            tts = gTTS(text=text, lang='ko', slow=False)
            tts.save(temp_mp3)
            
            # Then convert to WAV format for comparison
            y, sr = librosa.load(temp_mp3, sr=None)
            sf.write(reference_file, y, sr)
            
            # Remove temp mp3 file if conversion successful
            if os.path.exists(reference_file) and os.path.exists(temp_mp3):
                try:
                    os.remove(temp_mp3)
                except:
                    pass
        
        # Play the reference audio
        play_audio(reference_file)
        
        # Set up the recording parameters
        recording_seconds = 5  # Default to 5 seconds
        sample_rate = 44100
        channels = 1
        
        # Record audio
        print(f"\nNow it's your turn! Recording for {recording_seconds} seconds...")
        print("Speak the Korean text...")
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        # Open stream
        stream = p.open(format=pyaudio.paInt16,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=1024)
        
        # Start recording with countdown
        frames = []
        for i in range(recording_seconds, 0, -1):
            print(f"{i}...", end=" ", flush=True)
            time.sleep(1)
            data = stream.read(sample_rate)
            frames.append(data)
        
        print("\nRecording completed!")
        
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save the recording to user recordings directory
        wf = wave.open(user_file, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # print(f"\nRecording saved to: {user_file}")
        
        # Compare user's pronunciation with reference audio
        similarity_score = compare_audio(user_file, reference_file)
        
        if similarity_score is not None:
            print(f"\n[🎯] Pronunciation Match Score: {similarity_score}%")
            if similarity_score > 85:
                print("[🔥] Excellent pronunciation!")
            elif similarity_score > 65:
                print("[✅] Good, but could be smoother.")
            else:
                print("[⚠️] Try again — focus on clarity and pacing.")
                
            # Save score to a history file for tracking progress
            try:
                history_file = os.path.join(RECORDINGS_DIR, "pronunciation_history.json")
                history_data = []
                
                # Load existing history if available
                if os.path.exists(history_file):
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history_data = json.load(f)
                
                # Add new entry
                history_data.append({
                    "timestamp": timestamp,
                    "text": text,
                    "score": similarity_score,
                    "user_recording": user_filename,
                    "reference_recording": reference_filename
                })
                
                # Save updated history
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump(history_data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Error saving pronunciation history: {e}")
        
        # Playback options
        while True:
            choice = input("\nOptions:\n1. Listen to your recording\n2. Listen to correct pronunciation\n3. Try again\n4. Return to quiz\nChoose (1-4): ")
            
            if choice == '1':
                print("\nPlaying your recording...")
                play_audio(user_file)
            elif choice == '2':
                print("\nPlaying correct pronunciation...")
                play_audio(reference_file)
            elif choice == '3':
                # Clean up pygame mixer before recursive call
                pygame.mixer.quit()
                pygame.mixer.init()
                # Recursive call to practice again
                return practice_pronunciation(text)
            elif choice == '4':
                break
            else:
                print("Invalid option. Please choose 1, 2, 3, or 4.")
        
    except Exception as e:
        print(f"Error in pronunciation practice: {e}")
        print("Returning to quiz...")
    
    return