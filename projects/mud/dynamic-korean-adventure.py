import os
import time
import json
import requests

class KoreanAdventure:
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "llama3" # Change to your preferred model
        self.current_room = "start"
        self.inventory = []
        self.discovered_words = set()
        self.game_running = True
        
        # Game world will be dynamically generated
        self.rooms = {}
        self.characters = {}
        self.items = {}
        
        # Korean words to teach (expand as needed)
        self.korean_words = [
            {"hangul": "바람", "meaning": "wind"},
            {"hangul": "의자", "meaning": "chair"},
            {"hangul": "책", "meaning": "book"},
            {"hangul": "문", "meaning": "door"},
            {"hangul": "차", "meaning": "tea"},
            {"hangul": "새", "meaning": "bird"},
            {"hangul": "달", "meaning": "moon"},
            {"hangul": "물", "meaning": "water"},
            {"hangul": "나무", "meaning": "tree"},
            {"hangul": "꽃", "meaning": "flower"}
        ]
        self.used_words = []

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def generate_game_world(self):
        """Generate the initial game world using the LLM."""
        prompt = """
        Create a cozy, magical text adventure game world for Korean language learning. 
        The world should have 4 interconnected rooms. Each room should have:
        1. A name
        2. A short description that can incorporate a Korean word
        3. Available exits (directions to other rooms)
        4. 1-2 items that can be picked up
        5. One character to talk to

        Provide the response as valid JSON with this structure:
        {
          "rooms": {
            "room_id": {
              "name": "Room Name",
              "description_template": "Room description with a <KOREAN> placeholder.",
              "exits": {"north": "other_room_id", "south": "another_room_id", ...},
              "items": ["item1", "item2"],
              "characters": ["character1"]
            },
            ...more rooms...
          },
          "items": {
            "item1": "Description of item1",
            ...more items...
          },
          "characters": {
            "character1": {
              "description": "Description of the character",
              "dialogue_template": "Character dialogue with a <KOREAN> placeholder."
            },
            ...more characters...
          }
        }

        The world should be whimsical and magical, like a language-learning version of Zork.
        Make sure all room exits connect properly (if room A has a north exit to room B, then room B should have a south exit to room A).
        """

        try:
            response = self.query_llm(prompt)
            world_data = json.loads(response)
            
            # Validate and fix connections if needed
            self.rooms = world_data["rooms"]
            self.items = world_data["items"]
            self.characters = world_data["characters"]
            
            # Set starting room
            self.current_room = list(self.rooms.keys())[0]
            
            return True
        except Exception as e:
            print(f"Error generating game world: {e}")
            print("Using fallback world instead...")
            self._generate_fallback_world()
            return False

    def _generate_fallback_world(self):
        """Generate a fallback world if LLM fails."""
        self.rooms = {
            "garden": {
                "name": "Enchanted Garden",
                "description_template": "You stand in a beautiful garden where a gentle <KOREAN> rustles the leaves.",
                "exits": {"north": "cottage", "east": "forest"},
                "items": ["flower"],
                "characters": ["cat"]
            },
            "cottage": {
                "name": "Cozy Cottage",
                "description_template": "A warm cottage with a crackling fire. A comfortable <KOREAN> sits by the window.",
                "exits": {"south": "garden", "east": "library"},
                "items": ["book"],
                "characters": ["old_woman"]
            },
            "forest": {
                "name": "Whispering Forest",
                "description_template": "Tall trees surround you as a <KOREAN> sings somewhere above.",
                "exits": {"west": "garden", "north": "library"},
                "items": ["mushroom"],
                "characters": ["fox"]
            },
            "library": {
                "name": "Ancient Library",
                "description_template": "Shelves of books reach to the ceiling. A magical <KOREAN> glows faintly on a pedestal.",
                "exits": {"west": "cottage", "south": "forest"},
                "items": ["scroll"],
                "characters": ["scholar"]
            }
        }
        
        self.items = {
            "flower": "A beautiful flower with petals that shimmer in the light.",
            "book": "A small book with Korean phrases for travelers.",
            "mushroom": "A curious blue mushroom that seems to glow slightly.",
            "scroll": "An ancient scroll with Korean characters written in gold ink."
        }
        
        self.characters = {
            "cat": {
                "description": "A black cat with intelligent eyes watches you curiously.",
                "dialogue_template": "The cat purrs and says, 'Find the <KOREAN> that leads to wisdom.'"
            },
            "old_woman": {
                "description": "An elderly woman rocks gently in her chair.",
                "dialogue_template": "The woman smiles and says, 'Would you like some <KOREAN>, dear traveler?'"
            },
            "fox": {
                "description": "A red fox with unusually bright eyes sits on a tree stump.",
                "dialogue_template": "The fox tilts its head and says, 'The <KOREAN> reveals hidden paths.'"
            },
            "scholar": {
                "description": "A scholarly figure in robes examines an ancient manuscript.",
                "dialogue_template": "The scholar looks up and says, 'Knowledge is like <KOREAN> - it flows freely.'"
            }
        }
        
        self.current_room = "garden"

    def get_next_korean_word(self):
        """Get the next Korean word to teach."""
        available_words = [w for w in self.korean_words if w not in self.used_words]
        
        # If all words have been used, start over
        if not available_words:
            # Reset used words but keep the last used word to avoid repetition
            last_word = self.used_words[-1] if self.used_words else None
            self.used_words = [last_word] if last_word else []
            available_words = [w for w in self.korean_words if w not in self.used_words]
        
        word = available_words[0]
        self.used_words.append(word)
        self.discovered_words.add(word["hangul"])
        return word

    def display_room(self):
        """Display the current room information."""
        if self.current_room not in self.rooms:
            print(f"Error: Room '{self.current_room}' not found!")
            return
            
        room = self.rooms[self.current_room]
        
        # Get Korean word for this room
        korean_word = self.get_next_korean_word()
        
        self.clear_screen()
        print(f"\n=== Today's word: {korean_word['hangul']} ({korean_word['meaning']}) ===\n")
        print(f"【 {room['name']} 】")
        
        # Replace placeholder with Korean word
        description = room["description_template"].replace("<KOREAN>", f"\033[1m{korean_word['hangul']}\033[0m")
        print(description)
        
        # Display exits
        exits = ", ".join(room["exits"].keys())
        print(f"\nExits: {exits}")
        
        # Display items in the room
        items_in_room = [item for item in room.get("items", [])]
        if items_in_room:
            items_str = ", ".join(items_in_room)
            print(f"Items: {items_str}")
        
        # Display characters in the room
        chars_in_room = [self.characters[char]["description"] for char in room.get("characters", [])]
        if chars_in_room:
            for char_desc in chars_in_room:
                print(char_desc)
                
        print("\n")

    def handle_command(self, command):
        """Process the player's command."""
        parts = command.lower().split()
        
        if not parts:
            return
            
        action = parts[0]
        
        if action == "look":
            # Just redisplay the room
            pass
            
        elif action == "move" and len(parts) > 1:
            direction = parts[1]
            self.move_player(direction)
            
        elif action == "take" and len(parts) > 1:
            item = parts[1]
            self.take_item(item)
            
        elif action == "talk" and len(parts) > 1:
            character = parts[1]
            self.talk_to_character(character)
            
        elif action == "inventory":
            self.show_inventory()
            
        elif action == "help":
            self.show_help()
            
        elif action == "exit" or action == "quit":
            self.game_running = False
            print("Thank you for playing! 안녕히 가세요 (Goodbye)!")
            
        else:
            # Use LLM to understand unusual commands
            self.handle_custom_command(command)

    def handle_custom_command(self, command):
        """Handle custom commands using the LLM."""
        prompt = f"""
        In our Korean learning text adventure game, the player has entered this command:
        "{command}"
        
        The standard commands are:
        - look: Look around the current room
        - move [direction]: Move in a direction
        - take [item]: Pick up an item
        - talk [character]: Talk to a character
        - inventory: Check inventory
        - help: Show help menu
        
        The player is currently in a room called "{self.rooms[self.current_room]['name']}".
        
        If this command seems like it might be a valid action in an adventure game, 
        respond with a JSON object in this format:
        {{
          "command_type": "[standard_command]",
          "parameters": "[relevant_parameters]",
          "fallback_message": "A response if this can't be mapped to a standard command"
        }}
        
        For example, if they typed "grab flower", respond with:
        {{
          "command_type": "take",
          "parameters": "flower",
          "fallback_message": ""
        }}
        
        Or if they typed "what's in my bag?", respond with:
        {{
          "command_type": "inventory",
          "parameters": "",
          "fallback_message": ""
        }}
        
        If it can't be mapped to a standard command, provide a helpful, brief message:
        {{
          "command_type": "unknown",
          "parameters": "",
          "fallback_message": "I don't understand that. Try 'help' to see available commands."
        }}
        
        Return only the JSON, nothing else.
        """
        
        try:
            response = self.query_llm(prompt)
            result = json.loads(response)
            
            if result["command_type"] == "unknown":
                print(result["fallback_message"])
                time.sleep(1.5)
                return
                
            # Map the interpreted command to a standard command
            if result["command_type"] == "take":
                self.take_item(result["parameters"])
            elif result["command_type"] == "move":
                self.move_player(result["parameters"])
            elif result["command_type"] == "talk":
                self.talk_to_character(result["parameters"])
            elif result["command_type"] == "inventory":
                self.show_inventory()
            elif result["command_type"] == "look":
                pass  # Will redisplay the room naturally
            elif result["command_type"] == "help":
                self.show_help()
            else:
                print("I don't understand that command. Type 'help' for a list of commands.")
                time.sleep(1.5)
                
        except Exception as e:
            print("I don't understand that command. Type 'help' for a list of commands.")
            time.sleep(1.5)

    def move_player(self, direction):
        """Move the player in the specified direction."""
        room = self.rooms[self.current_room]
        
        if direction in room["exits"]:
            self.current_room = room["exits"][direction]
        else:
            print(f"You can't go {direction} from here.")
            time.sleep(1.5)

    def take_item(self, item_name):
        """Allow the player to pick up an item."""
        room = self.rooms[self.current_room]
        
        if item_name in room.get("items", []):
            self.inventory.append(item_name)
            room["items"].remove(item_name)
            print(f"You picked up the {item_name}.")
            
            # Display the item description
            if item_name in self.items:
                print(self.items[item_name])
            
            time.sleep(1.5)
        else:
            print(f"There's no {item_name} here.")
            time.sleep(1.5)

    def talk_to_character(self, character_name):
        """Talk to a character in the room."""
        room = self.rooms[self.current_room]
        
        if character_name in room.get("characters", []):
            character = self.characters[character_name]
            
            # Get Korean word for this dialogue
            korean_word = self.get_next_korean_word()
            
            # Replace placeholder with Korean word
            dialogue = character["dialogue_template"].replace("<KOREAN>", f"\033[1m{korean_word['hangul']}\033[0m")
            print(f"\n{dialogue}")
            print(f"({korean_word['hangul']} means '{korean_word['meaning']}')")
            
            input("\nPress Enter to continue...")
        else:
            print(f"There's no {character_name} here to talk to.")
            time.sleep(1.5)

    def show_inventory(self):
        """Display the player's inventory."""
        if not self.inventory:
            print("\nYour inventory is empty.")
        else:
            print("\nInventory:")
            for item in self.inventory:
                print(f"- {item}")
                if item in self.items:
                    print(f"  {self.items[item]}")
        
        input("\nPress Enter to continue...")

    def show_help(self):
        """Display the help menu."""
        print("\n=== Commands ===")
        print("look - Look around the current room")
        print("move [direction] - Move in a direction (north, south, east, west)")
        print("take [item] - Pick up an item")
        print("talk [character] - Talk to a character")
        print("inventory - Check your inventory")
        print("help - Show this help menu")
        print("exit - Quit the game")
        print("\nTip: The game will try to understand other commands too!")
        
        input("\nPress Enter to continue...")

    def show_intro(self):
        """Display the game introduction."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("                KOREAN LANGUAGE ADVENTURE")
        print("=" * 60)
        print("\nWelcome to a magical world where you'll learn Korean words!")
        print("Explore the world, talk to characters, and collect items.")
        print("Each room and character will teach you a new Korean word.")
        print("\nGenerating your unique adventure world...")
        
        success = self.generate_game_world()
        if success:
            print("World generation complete!")
        
        print("\nType 'help' anytime to see available commands.")
        print("\nPress Enter to begin your adventure...")
        input()

    def query_llm(self, prompt):
        """Send a query to the Ollama API and get a response."""
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(f"{self.ollama_url}/api/generate", json=data)
            if response.status_code == 200:
                return response.json()["response"]
            else:
                print(f"Error: Ollama API returned status code {response.status_code}")
                return None
        except Exception as e:
            print(f"Error communicating with Ollama: {e}")
            return None

    def run(self):
        """Main game loop."""
        self.show_intro()
        
        while self.game_running:
            self.display_room()
            command = input("> ")
            self.handle_command(command)
            
        print("\nYou've learned these Korean words:")
        for word in self.korean_words:
            if word["hangul"] in self.discovered_words:
                print(f"- {word['hangul']}: {word['meaning']}")

def test_ollama_connection(url="http://localhost:11434", model="llama3"):
    """Test connection to Ollama before starting the game."""
    print("Testing connection to Ollama...")
    try:
        response = requests.post(
            f"{url}/api/generate",
            json={"model": model, "prompt": "Say 'Connection successful'", "stream": False}
        )
        if response.status_code == 200:
            print("✅ Connected to Ollama successfully!")
            return True
        else:
            print(f"❌ Error: Ollama returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        print("Make sure Ollama is running with the command: ollama serve")
        print(f"And that you have the model '{model}' pulled (run: ollama pull {model})")
        return False

def main():
    # Test connection to Ollama
    ollama_url = "http://localhost:11434"  # Default Ollama URL
    model = "llama3"  # Default model
    
    # Allow custom URL and model from command line arguments
    import sys
    if len(sys.argv) > 1:
        ollama_url = sys.argv[1]
    if len(sys.argv) > 2:
        model = sys.argv[2]
    
    if test_ollama_connection(ollama_url, model):
        game = KoreanAdventure(ollama_url)
        game.model = model
        game.run()
    else:
        print("\nPlease start Ollama before running this game.")
        print(f"1. Run: ollama serve")
        print(f"2. Pull a model: ollama pull {model}")
        print(f"3. Then try again!")

if __name__ == "__main__":
    main()
