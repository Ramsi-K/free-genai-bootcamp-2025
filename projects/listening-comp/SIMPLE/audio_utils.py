import os
import librosa
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import tempfile
import hashlib
import pyaudio
import time
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import plays
from config import APP_CONFIG

def play_audio_with_speed(file_path, speed="normal"):
    """Play an audio file with speed control."""
    try:
        # Load speed configuration from app settings
        speed_factor = APP_CONFIG["speed_options"].get(speed, 1.0)
        
        # Load audio file
        audio = AudioSegment.from_file(file_path)
        
        # Apply speed modification if needed
        if speed_factor != 1.0:
            # Apply speed change using librosa and soundfile
            y, sr = librosa.load(file_path, sr=None)
            
            # Use librosa's time stretch function
            y_stretched = librosa.effects.time_stretch(y, rate=1/speed_factor)
            
            # Create a temporary file for the speed-adjusted audio
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            sf.write(temp_file.name, y_stretched, sr)
            
            # Play the temporary file
            playsound(temp_file.name, block=True)
            
            # Clean up
            temp_file.close()
            os.unlink(temp_file.name)
        else:
            # Play original audio if no speed adjustment
            playsound(file_path, block=True)
            
    except Exception as e:
        print(f"Error playing audio with speed control: {e}")

def text_to_speech_with_speed(text, speed="normal"):
    """Generate and play TTS with speed control."""
    try:
        # Choose appropriate voice based on application settings
        voice_name = APP_CONFIG.get("default_voice", "ko-KR-Neural2-C")
        
        # Create a temporary directory if it doesn't exist
        temp_dir = os.path.join(os.getcwd(), APP_CONFIG.get("temp_dir", "temp"))
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate unique filename for the audio
        filename = f"tts_{hashlib.md5(text.encode()).hexdigest()}.mp3"
        file_path = os.path.join(temp_dir, filename)
        
        # Check if we already have this audio file
        if not os.path.exists(file_path):
            # Set up TTS with appropriate voice
            tts = gTTS(text=text, lang='ko', slow=False)
            tts.save(file_path)
        
        # Play the audio with speed control
        play_audio_with_speed(file_path, speed)
        
        return file_path
        
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        return None

def practice_pronunciation(text):
    """Record user's pronunciation and compare with the correct pronunciation."""
    try:
        print("\n📝 Pronunciation Practice")
        print(f"Original text: {text}")
        
        # First play the correct pronunciation
        print("\nListen to the correct pronunciation...")
        text_to_speech_with_speed(text, "normal")
        
        # Set up the recording parameters
        recording_seconds = APP_CONFIG.get("recording_time", 5)
        sample_rate = APP_CONFIG.get("sample_rate", 44100)
        channels = APP_CONFIG.get("channels", 1)
        
        # Create a temporary directory for the recording
        temp_dir = os.path.join(os.getcwd(), APP_CONFIG.get("temp_dir", "temp"))
        os.makedirs(temp_dir, exist_ok=True)
        recording_file = os.path.join(temp_dir, "user_recording.wav")
        
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
        
        # Save the recording
        wf = wave.open(recording_file, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # Playback options
        while True:
            choice = input("\nOptions:\n1. Listen to your recording\n2. Listen to correct pronunciation\n3. Return to quiz\nChoose (1-3): ")
            
            if choice == '1':
                print("\nPlaying your recording...")
                playsound(recording_file, block=True)
            elif choice == '2':
                print("\nPlaying correct pronunciation...")
                text_to_speech_with_speed(text, "normal")
            elif choice == '3':
                break
            else:
                print("Invalid option. Please choose 1, 2, or 3.")
        
    except Exception as e:
        print(f"Error in pronunciation practice: {e}")
        print("Returning to quiz...")
    
    return