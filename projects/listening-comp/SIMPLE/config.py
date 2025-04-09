APP_CONFIG = {
    # Application settings
    "app_name": "Korean Listening Comprehension",
    "version": "1.0.0",
    
    # Directory configuration
    "data_dir": "data",
    "audio_dir": "audio",
    "temp_dir": "temp",
    "export_dir": "exports",
    "cache_dir": "cache",
    "progress_file": "progress.json",
    
    # Audio settings
    "speech_rate": "medium",  # slow, medium, fast
    "audio_formats": ["mp3", "wav"],
    "default_voice": "ko-KR-Neural2-C",
    "speed_options": {
        "normal": 1.0,
        "slow": 0.75
    },
    
    # Quiz settings
    "default_quiz_length": 5,
    "min_quiz_length": 3,
    "max_quiz_length": 10,
    "default_difficulty": "medium",
    
    # Difficulty levels configuration
    "difficulty_levels": {
        "easy": {
            "max_sentence_length": 15,
            "speech_rate": "slow",
            "max_questions": 3,
            "description": "Shorter sentences, slower playback"
        },
        "medium": {
            "max_sentence_length": 25,
            "speech_rate": "medium",
            "max_questions": 5,
            "description": "Standard difficulty"
        },
        "hard": {
            "max_sentence_length": 40,
            "speech_rate": "normal",
            "max_questions": 7,
            "description": "Longer sentences, more questions"
        }
    },
    
    # Model settings
    "default_model": "gpt2",
    "topik_question_count": 5,
    
    # Recording settings
    "recording_time": 5,  # seconds
    "sample_rate": 44100,  # Hz
    "channels": 1,
    
    # Anki export settings
    "anki_deck_name": "Korean Listening",
    "anki_note_type": "Basic",
    "anki_tags": ["korean", "listening"]
}