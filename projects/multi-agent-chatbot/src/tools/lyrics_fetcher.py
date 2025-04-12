"""
LyricsFetcher - An agent for retrieving and explaining Korean song lyrics

This agent helps users find Korean song lyrics, provides translations,
and explains cultural references and vocabulary.
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from src.agents.base import OllamaBaseAgent


class LyricsFetcher(OllamaBaseAgent):
    """
    Agent for retrieving and explaining Korean song lyrics
    """

    def __init__(
        self,
        model: str = "kimjk/llama3.2-korean:latest",
        temperature: float = 0.7,
        verbose: bool = True,
    ):
        """
        Initialize the Lyrics Fetcher Agent

        Args:
            model: The model to use for generation
            temperature: Controls randomness (0.0-1.0)
            verbose: Whether to print verbose output
        """
        # Initialize agent with role and goal
        super().__init__(
            role="Korean Music and Lyrics Specialist",
            goal="Help users understand Korean songs and their lyrics",
            backstory="""You are a Korean music enthusiast with extensive knowledge 
            of K-pop, K-indie, and traditional Korean music. You can find lyrics, 
            explain their meanings, and highlight interesting vocabulary and cultural references.""",
            model=model,
            temperature=temperature,
            verbose=verbose,
            allow_delegation=False,
        )

    def search_lyrics(self, song_title, artist=None):
        """
        Search for Korean song lyrics using a search engine

        Args:
            song_title: Title of the song
            artist: Optional artist name

        Returns:
            A formatted string with the search results
        """
        # Format search query
        search_query = f"{song_title}"
        if artist:
            search_query += f" {artist}"
        search_query += " lyrics korean english"

        # Use DuckDuckGo for search
        from duckduckgo_search import DDGS

        try:
            with DDGS() as ddgs:
                results = list(
                    ddgs.text(
                        search_query,
                        region="wt-wt",
                        safesearch="moderate",
                        max_results=3,
                    )
                )

            if not results:
                return "No lyrics found. Please try with a more specific song title or artist name."

            formatted_results = ""
            for i, result in enumerate(results, 1):
                formatted_results += f"Result {i}:\n"
                formatted_results += f"Title: {result.get('title', '')}\n"
                formatted_results += f"URL: {result.get('href', '')}\n\n"

            return formatted_results

        except Exception as e:
            return f"Error searching for lyrics: {str(e)}"

    def execute_task(self, task):
        """
        Execute the lyrics task

        Args:
            task: The task to execute, which should contain user's query about lyrics

        Returns:
            String response with lyrics information
        """
        query = task.input

        # Extract song title and artist using a simple pattern matching approach
        # Look for patterns like "find lyrics for [song] by [artist]"
        song_pattern = re.compile(
            r"lyrics? (?:for|to|of) ['\"](.*?)['\"](?: by (.+?))?(?:\?|$|\.)"
        )
        song_match = song_pattern.search(query)

        # Alternative pattern: "[song title] lyrics"
        alt_pattern = re.compile(r"['\"](.*?)['\"] lyrics")
        alt_match = alt_pattern.search(query)

        # Extract song and artist info
        if song_match:
            song_title = song_match.group(1)
            artist = song_match.group(2) if song_match.group(2) else None
        elif alt_match:
            song_title = alt_match.group(1)
            artist = None
        else:
            # If no clear pattern, ask the LLM to extract the song and artist
            system_prompt = """
            Extract the song title and artist from the user's query.
            If they're not provided, respond with "Unknown" for the missing information.
            Format your response as "Song: [song title], Artist: [artist name]"
            """

            extraction_result = self.generate_response(
                prompt=f"Extract song and artist from: {query}",
                system_prompt=system_prompt,
            )

            # Parse the extraction result
            song_extract = re.search(r"Song: (.*?),", extraction_result)
            artist_extract = re.search(r"Artist: (.*?)$", extraction_result)

            song_title = song_extract.group(1) if song_extract else "Unknown"
            artist = artist_extract.group(1) if artist_extract else None

            if song_title == "Unknown":
                return "I couldn't identify a specific song in your request. Please specify a song title, for example: 'Find lyrics for Gangnam Style by PSY'"

        # Search for lyrics
        search_results = self.search_lyrics(song_title, artist)

        # Generate response using the Ollama model
        system_prompt = """
        You are an expert on Korean music and lyrics. Based on the search results 
        provided, generate a helpful response about the requested song.
        
        If specific lyrics aren't available in the search results, provide general 
        information about the song, artist, and its cultural significance.
        
        Include:
        1. Basic information about the song and artist
        2. Cultural context or interesting facts
        3. Suggest how the user could learn vocabulary from this song
        
        When actual lyrics are mentioned, display them in a clear format with 
        Korean text followed by English translation when available.
        """

        final_response = self.generate_response(
            prompt=f"User query about Korean lyrics: {query}\n\nSearch results:\n{search_results}\n\nResponse:",
            system_prompt=system_prompt,
        )

        return final_response
