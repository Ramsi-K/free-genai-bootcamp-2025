import os
import json
import time
import uuid
import logging
import tempfile
import numpy as np
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import soundfile as sf
from pydub import AudioSegment
import torch
from transformers import AutoProcessor, AutoModel

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
DATA_DIR = os.environ.get('DATA_DIR', '/shared/data')
AUDIO_DIR = os.environ.get('AUDIO_DIR', '/shared/data/audio')
USE_GPU = os.environ.get('USE_GPU', 'true').lower() == 'true'

# Create directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# Check if GPU is available
if USE_GPU and torch.cuda.is_available():
    DEVICE = torch.device("cuda")
    logger.info("Using GPU for audio processing")
else:
    DEVICE = torch.device("cpu")
    logger.info("Using CPU for audio processing")

# Initialize TTS model
def initialize_tts_model():
    try:
        # Try to load MeloTTS for Korean TTS
        # If MeloTTS is not available, we'll use a fallback method
        processor = AutoProcessor.from_pretrained("PixelCat/melotts-korean-base")
        model = AutoModel.from_pretrained("PixelCat/melotts-korean-base").to(DEVICE)
        return {
            "processor": processor, 
            "model": model, 
            "initialized": True
        }
    except Exception as e:
        logger.error(f"Failed to initialize TTS model: {e}")
        return {"initialized": False}

# Initialize the TTS model
tts_model = initialize_tts_model()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    """Convert text to speech."""
    try:
        data = request.json
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        voice = data.get('voice', 'default')  # Future option for different voices
        
        if not tts_model["initialized"]:
            return jsonify({'error': 'TTS model not initialized'}), 500
        
        # Process text with TTS model
        inputs = tts_model["processor"](
            text=text, 
            return_tensors="pt",
        ).to(DEVICE)
        
        with torch.no_grad():
            output = tts_model["model"].generate(
                **inputs,
                do_sample=True,
            )
        
        # Get the audio samples
        audio_samples = output.audio_values.cpu().numpy().squeeze()
        
        # Create a unique filename
        filename = f"{uuid.uuid4()}.wav"
        filepath = os.path.join(AUDIO_DIR, filename)
        
        # Save the audio file
        sf.write(filepath, audio_samples, 24000)  # Assuming 24kHz sample rate
        
        return jsonify({
            'success': True,
            'audio_path': filepath,
            'audio_url': f"/api/audio/{filename}"
        })
    
    except Exception as e:
        logger.error(f"Error generating TTS: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-questions/<video_id>', methods=['POST'])
def process_questions(video_id):
    """Process questions for a video, generating audio for each question."""
    try:
        # Get questions file
        questions_path = os.path.join(DATA_DIR, f"{video_id}_questions.json")
        if not os.path.exists(questions_path):
            return jsonify({'error': 'No questions found for this video'}), 404
        
        with open(questions_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        questions = questions_data.get('questions', [])
        if not questions:
            return jsonify({'error': 'No questions found in the data'}), 400
        
        # Process each question
        for i, question in enumerate(questions):
            # Generate audio for the question
            question_text = question.get('question', '')
            if question_text:
                try:
                    # Call the TTS endpoint
                    tts_response = text_to_speech()
                    tts_data = tts_response.get_json()
                    
                    if tts_response.status_code == 200 and tts_data.get('success'):
                        # Add audio information to the question
                        questions[i]['audio_url'] = tts_data.get('audio_url')
                except Exception as e:
                    logger.error(f"Error generating audio for question {i}: {e}")
        
        # Update questions file with audio URLs
        questions_data['questions'] = questions
        with open(questions_path, 'w', encoding='utf-8') as f:
            json.dump(questions_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'message': f"Processed {len(questions)} questions with audio",
            'questions': questions
        })
    
    except Exception as e:
        logger.error(f"Error processing questions for video {video_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/audio/<filename>', methods=['GET'])
def get_audio(filename):
    """Retrieve an audio file."""
    try:
        filepath = os.path.join(AUDIO_DIR, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'Audio file not found'}), 404
        
        return send_file(
            filepath,
            mimetype='audio/wav',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        logger.error(f"Error retrieving audio file {filename}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/extract-audio/<video_id>', methods=['POST'])
def extract_audio_segment(video_id):
    """Extract audio segment from a video."""
    try:
        data = request.json
        if not data or 'start' not in data or 'end' not in data:
            return jsonify({'error': 'Start and end times are required'}), 400
        
        start_time = float(data['start'])
        end_time = float(data['end'])
        
        # Check if we have the full audio file
        audio_file = os.path.join(AUDIO_DIR, f"{video_id}_full.wav")
        
        if not os.path.exists(audio_file):
            # If we don't have the audio, check if we can get it from the transcript metadata
            file_path = os.path.join(DATA_DIR, f"{video_id}.json")
            if not os.path.exists(file_path):
                return jsonify({'error': 'Video data not found'}), 404
            
            # This would normally download the audio from YouTube or another source
            # For this example, we'll return an error as we don't have the audio
            return jsonify({'error': 'Full audio not available for this video'}), 400
        
        # Load audio file
        audio = AudioSegment.from_wav(audio_file)
        
        # Convert start and end times to milliseconds
        start_ms = int(start_time * 1000)
        end_ms = int(end_time * 1000)
        
        # Extract segment
        segment = audio[start_ms:end_ms]
        
        # Create a unique filename
        segment_filename = f"{video_id}_{start_ms}_{end_ms}.wav"
        segment_filepath = os.path.join(AUDIO_DIR, segment_filename)
        
        # Export segment
        segment.export(segment_filepath, format="wav")
        
        return jsonify({
            'success': True,
            'audio_path': segment_filepath,
            'audio_url': f"/api/audio/{segment_filename}"
        })
    
    except Exception as e:
        logger.error(f"Error extracting audio segment: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/audio-questions/<video_id>', methods=['GET'])
def get_audio_questions(video_id):
    """Get questions with audio URLs for a video."""
    try:
        questions_path = os.path.join(DATA_DIR, f"{video_id}_questions.json")
        if not os.path.exists(questions_path):
            return jsonify({'error': 'No questions found for this video'}), 404
        
        with open(questions_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        # Filter questions to include only those with audio
        questions = questions_data.get('questions', [])
        audio_questions = [q for q in questions if 'audio_url' in q]
        
        return jsonify({
            'success': True,
            'questions': audio_questions,
            'count': len(audio_questions)
        })
    
    except Exception as e:
        logger.error(f"Error getting audio questions for video {video_id}: {e}")
        return jsonify({'error': str(e)}), 500

# Fallback method for TTS if transformers model is not available
def fallback_tts(text):
    """Fallback method for TTS using an external service."""
    try:
        # Use an external API or default sound file
        filename = f"{uuid.uuid4()}.wav"
        filepath = os.path.join(AUDIO_DIR, "fallback.wav")
        
        # For demo purposes, we'll create a simple sine wave
        sample_rate = 24000
        duration = 2.0  # seconds
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
        
        # Save to file
        sf.write(filepath, audio, sample_rate)
        
        return {
            'success': True,
            'audio_path': filepath,
            'audio_url': f"/api/audio/fallback.wav"
        }
    except Exception as e:
        logger.error(f"Error in fallback TTS: {e}")
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)