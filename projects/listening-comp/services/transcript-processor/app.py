import os
import json
import re
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import requests
from langdetect import detect
import pandas as pd
from pytube import YouTube
from comps import MicroService, ServiceOrchestrator, ServiceType, ServiceRoleType
from comps.cores.proto.api_protocol import (
    TranscriptRequest,
    TranscriptResponse,
    ServiceException
)

app = Flask(__name__)
CORS(app)

# Configuration
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', '/shared/data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize ServiceOrchestrator
service_orchestrator = ServiceOrchestrator(device=DEVICE)

# Define service dependencies
question_service = MicroService(
    name="question_service",
    host="question-module",  # Docker service name
    port=5001,
    endpoint="/api/generate-questions",
    service_type=ServiceType.PROCESSOR,
    use_remote_service=True,
    device=DEVICE
)

audio_service = MicroService(
    name="audio_service",
    host="audio-module",  # Docker service name
    port=5002,
    endpoint="/api/extract-audio",
    service_type=ServiceType.AUDIO,
    use_remote_service=True,
    device=DEVICE
)

# Register services
service_orchestrator.add(question_service)
service_orchestrator.add(audio_service)

def extract_video_id(url):
    """Extract YouTube video ID from URL."""
    video_id = None
    if 'youtube.com/watch?v=' in url:
        video_id = url.split('youtube.com/watch?v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[1].split('?')[0]
    return video_id

def get_video_metadata(video_id):
    """Get video metadata using pytube."""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        yt = YouTube(url)
        return {
            'title': yt.title,
            'author': yt.author,
            'description': yt.description,
            'length': yt.length,
            'publish_date': str(yt.publish_date) if yt.publish_date else None,
            'views': yt.views
        }
    except Exception as e:
        app.logger.error(f"Error getting metadata for {video_id}: {e}")
        return {
            'title': 'Unknown',
            'author': 'Unknown',
            'description': '',
            'length': 0,
            'publish_date': None,
            'views': 0
        }

def is_korean_content(text):
    """Check if the content is primarily Korean."""
    try:
        lang = detect(text)
        return lang == 'ko'
    except:
        # If detection fails, check for Korean characters
        korean_char_count = len(re.findall(r'[\uAC00-\uD7A3]', text))
        return korean_char_count > len(text) * 0.3  # If more than 30% are Korean characters

def process_transcript(transcript):
    """Process and clean transcript entries."""
    formatter = TextFormatter()
    transcript_text = formatter.format_transcript(transcript)
    
    # Additional processing for Korean transcripts
    transcript_text = re.sub(r'\s+', ' ', transcript_text).strip()
    
    # Create structured transcript with timestamps
    structured_transcript = []
    for entry in transcript:
        structured_transcript.append({
            'start': entry['start'],
            'duration': entry['duration'],
            'text': entry['text'].strip()
        })
    
    return transcript_text, structured_transcript

def segment_transcript(structured_transcript, segment_duration=30):
    """Segment the transcript into chunks of approximately segment_duration seconds."""
    segments = []
    current_segment = []
    current_duration = 0
    segment_start = 0
    
    for entry in structured_transcript:
        if current_duration == 0:
            segment_start = entry['start']
            
        current_segment.append(entry)
        current_duration += entry['duration']
        
        if current_duration >= segment_duration:
            segment_text = ' '.join([e['text'] for e in current_segment])
            segments.append({
                'start': segment_start,
                'end': segment_start + current_duration,
                'duration': current_duration,
                'text': segment_text
            })
            current_segment = []
            current_duration = 0
    
    # Add the last segment if it's not empty
    if current_segment:
        segment_text = ' '.join([e['text'] for e in current_segment])
        segments.append({
            'start': segment_start,
            'end': segment_start + current_duration,
            'duration': current_duration,
            'text': segment_text
        })
    
    return segments

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

# Add detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/api/process', methods=['POST'])
def process_video():
    """Process YouTube video and extract transcript."""
    try:
        data = request.json
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        video_id = extract_video_id(url)
        
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400

        # Try to get transcript with multiple language codes and auto-generated option
        for lang_code in ['ko', 'ko-KR']:
            try:
                # Try manual subtitles first
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang_code])
                break
            except:
                try:
                    # Try auto-generated subtitles
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang_code], params={'as_generated': True})
                    break
                except:
                    continue
        else:
            return jsonify({'error': '한국어 자막을 찾을 수 없습니다. 자막이 있는 동영상을 선택하세요.'}), 400

        # Process transcript
        transcript_text, structured_transcript = process_transcript(transcript)
        
        # Check if content is primarily Korean
        if not is_korean_content(transcript_text):
            logger.error(f"Content not primarily Korean for video {video_id}")
            return jsonify({'error': 'Content is not primarily in Korean'}), 400
        
        # Get video metadata
        metadata = get_video_metadata(video_id)
        
        # Segment transcript for easier processing
        segments = segment_transcript(structured_transcript)
        
        # Save processed data
        result = {
            'video_id': video_id,
            'metadata': metadata,
            'full_transcript': transcript_text,
            'structured_transcript': structured_transcript,
            'segments': segments
        }
        
        # Save to file
        output_path = os.path.join(OUTPUT_DIR, f"{video_id}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'video_id': video_id,
            'metadata': metadata,
            'transcript_length': len(transcript_text),
            'segments_count': len(segments),
            'file_path': output_path
        })
    
    except Exception as e:
        logger.error(f"Error processing video {video_id}: {str(e)}", exc_info=True)
        return jsonify({'error': '비디오 처리 중 오류가 발생했습니다. 다른 URL을 시도해보세요.'}), 500

@app.route('/api/videos', methods=['GET'])
def list_videos():
    """List all processed videos."""
    try:
        files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.json')]
        videos = []
        
        for file in files:
            file_path = os.path.join(OUTPUT_DIR, file)
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
                app.logger.error(f"Error reading file {file}: {str(e)}")
        
        return jsonify({
            'success': True,
            'count': len(videos),
            'videos': videos
        })
    
    except Exception as e:
        app.logger.error(f"Error listing videos: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/video/<video_id>', methods=['GET'])
def get_video_data(video_id):
    """Get processed data for a specific video."""
    try:
        file_path = os.path.join(OUTPUT_DIR, f"{video_id}.json")
        if not os.path.exists(file_path):
            return jsonify({'error': 'Video not found'}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify({
            'success': True,
            'data': data
        })
    
    except Exception as e:
        app.logger.error(f"Error getting video {video_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/video/<video_id>', methods=['DELETE'])
def delete_video(video_id):
    """Delete processed data for a specific video."""
    try:
        file_path = os.path.join(OUTPUT_DIR, f"{video_id}.json")
        if not os.path.exists(file_path):
            return jsonify({'error': 'Video not found'}), 404
        
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'message': f"Video {video_id} deleted successfully"
        })
    
    except Exception as e:
        app.logger.error(f"Error deleting video {video_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
