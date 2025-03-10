from typing import Dict, List, Optional
import re
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class VideoGuardrails:
    min_duration: int = 60  # Minimum video length in seconds
    max_duration: int = 900  # Maximum video length (15 minutes)
    min_transcript_length: int = 100  # Minimum transcript character length
    max_transcript_length: int = 5000  # Maximum transcript character length
    min_korean_ratio: float = 0.7  # Minimum ratio of Korean text
    blacklisted_channels: List[str] = None  # Channels to block
    rate_limit: int = 10  # Requests per minute
    requests: Dict[str, List[datetime]] = None  # Track request timestamps

    def __post_init__(self):
        self.blacklisted_channels = self.blacklisted_channels or []
        self.requests = {}

    def check_rate_limit(self, ip_address: str) -> bool:
        """Check if IP has exceeded rate limit."""
        now = datetime.now()
        if ip_address not in self.requests:
            self.requests[ip_address] = []
        
        # Remove old requests
        self.requests[ip_address] = [
            ts for ts in self.requests[ip_address] 
            if now - ts < timedelta(minutes=1)
        ]
        
        if len(self.requests[ip_address]) >= self.rate_limit:
            return False
        
        self.requests[ip_address].append(now)
        return True

    def validate_video_metadata(self, metadata: Dict) -> Optional[str]:
        """Validate video metadata."""
        if metadata.get('length', 0) < self.min_duration:
            return f"비디오가 너무 짧습니다. 최소 {self.min_duration}초 이상이어야 합니다."
        
        if metadata.get('length', 0) > self.max_duration:
            return f"비디오가 너무 깁니다. 최대 {self.max_duration}초까지 가능합니다."
        
        if metadata.get('author', '') in self.blacklisted_channels:
            return "이 채널의 콘텐츠는 허용되지 않습니다."
        
        return None

    def validate_transcript(self, transcript_text: str) -> Optional[str]:
        """Validate transcript content."""
        if len(transcript_text) < self.min_transcript_length:
            return "자막이 너무 짧습니다."
        
        if len(transcript_text) > self.max_transcript_length:
            return "자막이 너무 깁니다."
        
        # Count Korean characters
        korean_chars = len(re.findall(r'[\uAC00-\uD7A3]', transcript_text))
        total_chars = len(re.sub(r'\s', '', transcript_text))
        
        if total_chars > 0 and korean_chars / total_chars < self.min_korean_ratio:
            return "한국어 내용이 충분하지 않습니다."
        
        return None

    def validate_segments(self, segments: List[Dict]) -> Optional[str]:
        """Validate transcript segments."""
        if not segments:
            return "자막 세그먼트가 없습니다."
        
        for segment in segments:
            if segment['duration'] < 1:
                return "자막 세그먼트가 너무 짧습니다."
            if not segment['text'].strip():
                return "빈 자막 세그먼트가 있습니다."
        
        return None
