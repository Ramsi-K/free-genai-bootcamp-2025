from crewai import Crew, Task
from crew import KoreanTutoringCrew
import re
import random
import crewai

print(crewai.__version__)


def detect_task_type(user_input):
    """Detect which task type is most appropriate for the given input"""

    # Convert input to lowercase for easier matching
    input_lower = user_input.lower()

    # Check for vector database query keywords
    vector_db_keywords = [
        "example",
        "similar",
        "find",
        "retrieve",
        "show me",
        "example of",
        "database",
        "search database",
    ]
    if any(keyword in input_lower for keyword in vector_db_keywords):
        return "vector_db_query"

    # Check for web search keywords
    web_search_keywords = [
        "search",
        "look up",
        "google",
        "find online",
        "web",
        "internet",
        "recent",
        "news",
    ]
    if any(keyword in input_lower for keyword in web_search_keywords):
        return "web_search"

    # Check for idiom/proverb/cultural keywords
    idiom_keywords = [
        "proverb",
        "saying",
        "idiom",
        "cultural",
        "tradition",
        "metaphor",
        "wisdom",
        "속담",
    ]
    if any(keyword in input_lower for keyword in idiom_keywords):
        return "idiom_lookup"

    # Check for lyrics keywords
    lyrics_keywords = [
        "song",
        "lyrics",
        "music",
        "k-pop",
        "kpop",
        "sing",
        "가사",
        "노래",
    ]
    if any(keyword in input_lower for keyword in lyrics_keywords):
        return "lyrics"

    # If asking about Korean content without specific request type identifiers, use grammar
    korean_pattern = re.compile(r"[\uac00-\ud7a3]")  # Korean Unicode range
    if korean_pattern.search(input_lower) or "korean" in input_lower:
        return "grammar_question"

    # Default to grammar questions
    return "grammar_question"


def select_agent_by_query(user_input):
    """Select which agent should handle the query based on content"""

    input_lower = user_input.lower()

    # Topics that AhjummaGPT handles better
    ahjumma_topics = [
        "food",
        "김치",
        "cooking",
        "family",
        "practical",
        "daily",
        "서울",
        "시장",
    ]

    # Topics that AhjussiGPT handles better
    ahjussi_topics = [
        "history",
        "tradition",
        "philosophy",
        "proverb",
        "politics",
        "business",
        "wisdom",
    ]

    # Check if query matches ahjumma topics
    if any(topic in input_lower for topic in ahjumma_topics):
        return "ahjumma_gpt"

    # Check if query matches ahjussi topics
    if any(topic in input_lower for topic in ahjussi_topics):
        return "ahjussi_gpt"

    # If the query has a direct, forceful tone, send to ahjumma
    forceful_words = [
        "how do i",
        "explain",
        "tell me",
        "show me",
        "fast",
        "quick",
        "need to know",
    ]
    if any(word in input_lower for word in forceful_words):
        return "ahjumma_gpt"

    # If the query has a reflective, thoughtful tone, send to ahjussi
    thoughtful_words = [
        "why",
        "what is the reason",
        "philosophy",
        "meaning",
        "historical",
        "origins",
    ]
    if any(word in input_lower for word in thoughtful_words):
        return "ahjussi_gpt"

    # If nothing matches, randomly select
    return random.choice(["ahjumma_gpt", "ahjussi_gpt"])


def print_welcome():
    """Display welcome message and instructions"""
    print("\n" + "=" * 50)
    print("🇰🇷 Korean Language Learning Chatbot 🇰🇷".center(50))
    print("=" * 50)
    print("\nWelcome! I can help you learn Korean language and culture.")
    print("\nI can assist with:")
    print("  • Korean grammar explanations and examples")
    print("  • Korean proverbs, idioms, and cultural sayings")
    print("  • Finding relevant examples from my knowledge database")
    print("  • Web searches for Korean language topics")
    print("  • Korean song lyrics and their meanings")
    print("\nI have two personas:")
    print("  • 아줌마 (Ahjumma) - A direct, no-nonsense Korean auntie")
    print("  • 아저씨 (Ahjussi) - A wise, story-telling Korean uncle")
    print("\nCommands:")
    print("  • Type 'exit' or 'quit' to end the conversation")
    print("  • Type 'help' to see this information again")
    print("\nAsk me anything about Korean language or culture!")
    print("=" * 50)


def main():
    # Initialize the Korean tutoring crew
    korean_crew = KoreanTutoringCrew()
    crew = korean_crew.crew()

    # Display welcome message
    print_welcome()

    # Chat loop
    while True:
        # Get user input
        user_input = input("\nYou: ")

        # Check special commands
        if user_input.lower() in ["exit", "quit"]:
            print(
                "\n안녕히 가세요! (Goodbye!) Thank you for using the Korean Language Learning Chatbot!"
            )
            break

        if user_input.lower() == "help":
            print_welcome()
            continue

        if not user_input.strip():
            continue

        # Process the input with the crew
        try:
            # Detect which task type is most appropriate
            task_type = detect_task_type(user_input)

            # Create inputs dictionary for the crew kickoff
            inputs = {"query": user_input, "task_type": task_type}

            # Execute the crew with inputs - this matches the documentation pattern
            print("\nThinking... (this may take a moment)")
            response = crew.kickoff(inputs=inputs)

            # Determine which character to use for the response display
            if task_type == "grammar_question":
                print("\n아줌마 (Ahjumma):", response)
            else:
                print("\n아저씨 (Ahjussi):", response)

        except Exception as e:
            print(f"\nSorry, I encountered an error: {e}")
            print("Please try asking something else.")


if __name__ == "__main__":
    main()
