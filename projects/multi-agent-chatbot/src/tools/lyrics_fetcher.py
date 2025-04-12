# src/tools/lyrics_fetcher.py
import requests
from bs4 import BeautifulSoup
import re

class LyricsFetcher:
    def __init__(self):
        self.sites = {
            "genius": self.fetch_from_genius,
            "naver": self.fetch_from_naver
        }
        
    def fetch_from_genius(self, song_title, artist):
        """Fetch lyrics from Genius.com"""
        url = f"https://genius.com/{artist}-{song_title}-lyrics"
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            lyrics = soup.find("div", {"class": "Lyrics__Container-sc-1ynbvzw-2"}).text
            return lyrics
        return None

    def fetch_from_naver(self, song_title, artist):
        """Fetch lyrics from Naver Music"""
        url = f"https://music.naver.com/search/search.nhn?query={song_title}+{artist}"
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Add logic to extract lyrics from Naver Music
            return "Lyrics from Naver Music"
        return None

    def get_lyrics(self, song_title, artist, source="genius"):
        """Get song lyrics from specified source"""
        if source in self.sites:
            return self.sites[source](song_title, artist)
        return None