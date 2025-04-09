import os
import json
import time
from datetime import datetime
from config import APP_CONFIG

# Vocabulary file path
VOCAB_FILE = os.path.join(APP_CONFIG.get("data_dir", "data"), "vocabulary.json")

def save_vocabulary(new_words):
    """Save new vocabulary words to the vocabulary database."""
    try:
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(VOCAB_FILE), exist_ok=True)
        
        # Load existing vocabulary
        vocabulary = []
        if os.path.exists(VOCAB_FILE):
            with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
                vocabulary = json.load(f)
        
        # Timestamp for the new entries
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add new words to vocabulary
        for word_data in new_words:
            word = word_data.get("word", "").strip()
            if not word:
                continue
                
            context = word_data.get("context", "").strip()
            
            # Check if word already exists
            existing = next((item for item in vocabulary if item["word"] == word), None)
            
            if existing:
                # Update existing word with new context if different
                if context and context not in existing.get("contexts", []):
                    if "contexts" not in existing:
                        existing["contexts"] = []
                    existing["contexts"].append(context)
                    existing["updated_at"] = timestamp
            else:
                # Add new word
                vocabulary.append({
                    "word": word,
                    "contexts": [context] if context else [],
                    "created_at": timestamp,
                    "reviewed": 0
                })
        
        # Save updated vocabulary
        with open(VOCAB_FILE, 'w', encoding='utf-8') as f:
            json.dump(vocabulary, f, ensure_ascii=False, indent=2)
            
        return len(new_words)
        
    except Exception as e:
        print(f"Error saving vocabulary: {e}")
        return 0

def get_vocabulary_count():
    """Get the count of vocabulary words."""
    try:
        if os.path.exists(VOCAB_FILE):
            with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
                vocabulary = json.load(f)
            return len(vocabulary)
        return 0
    except Exception as e:
        print(f"Error getting vocabulary count: {e}")
        return 0

def browse_vocabulary():
    """Display the vocabulary list with context sentences."""
    try:
        if not os.path.exists(VOCAB_FILE):
            print("\nNo vocabulary saved yet.")
            return
        
        with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
            vocabulary = json.load(f)
        
        if not vocabulary:
            print("\nVocabulary list is empty.")
            return
        
        # Sort by most recently added
        vocabulary.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        page_size = 5
        total_pages = (len(vocabulary) + page_size - 1) // page_size
        current_page = 1
        
        while True:
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, len(vocabulary))
            
            print(f"\n📚 Vocabulary List (Page {current_page}/{total_pages})")
            print(f"Total words: {len(vocabulary)}")
            print("-" * 50)
            
            for i in range(start_idx, end_idx):
                word = vocabulary[i]
                print(f"{i+1}. {word['word']}")
                
                # Show contexts
                if word.get("contexts"):
                    print("   Context examples:")
                    for j, context in enumerate(word["contexts"][:2]):  # Show up to 2 contexts
                        print(f"   - {context}")
                    if len(word["contexts"]) > 2:
                        print(f"   ... and {len(word['contexts']) - 2} more examples")
                
                print()
            
            # Navigation options
            print("\nOptions:")
            if current_page > 1:
                print("P - Previous page")
            if current_page < total_pages:
                print("N - Next page")
            print("S - Search vocabulary")
            print("Q - Return to main menu")
            
            choice = input("\nEnter your choice: ").upper()
            
            if choice == 'P' and current_page > 1:
                current_page -= 1
            elif choice == 'N' and current_page < total_pages:
                current_page += 1
            elif choice == 'S':
                search_term = input("\nEnter search term: ").strip()
                if search_term:
                    search_results = [word for word in vocabulary if search_term.lower() in word["word"].lower()]
                    if search_results:
                        print(f"\nFound {len(search_results)} matching words:")
                        for i, word in enumerate(search_results[:10]):  # Show up to 10 results
                            print(f"{i+1}. {word['word']}")
                            if word.get("contexts"):
                                print(f"   Context: {word['contexts'][0]}")
                    else:
                        print("\nNo matching words found.")
                    input("\nPress Enter to continue...")
            elif choice == 'Q':
                break
            else:
                print("\nInvalid choice. Try again.")
                
    except Exception as e:
        print(f"Error browsing vocabulary: {e}")
        input("\nPress Enter to continue...")

