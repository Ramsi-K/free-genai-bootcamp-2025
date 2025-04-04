import requests
import time

VIDEO_URL = "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
VIDEO_ID = "YOUR_VIDEO_ID"  # Replace with the actual ID

# 1. Transcript Service
print("[1] Sending video URL to transcript processor...")
resp1 = requests.post(
    "http://localhost:5000/api/process", json={"video_url": VIDEO_URL}
)
print("Transcript processor response:", resp1.status_code)
time.sleep(3)  # wait for file write

# 2. Question Generator
print("\n[2] Sending video ID to question generator...")
resp2 = requests.post(
    "http://localhost:5001/api/questions", json={"video_id": VIDEO_ID}
)
print("Question generator response:", resp2.status_code)
time.sleep(3)

# 3. TTS Generator
print("\n[3] Triggering TTS for generated questions...")
resp3 = requests.post(
    "http://localhost:5002/api/generate-tts", json={"video_id": VIDEO_ID}
)
print("Audio module response:", resp3.status_code)

# 4. Check final output
print("\n[4] Fetching final processed question+audio data...")
resp4 = requests.get(
    f"http://localhost:5002/api/questions-with-audio/{VIDEO_ID}"
)
print("Output:")
print(resp4.json())
