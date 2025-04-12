import os
import time
import json
import requests

MODEL = "kimjk/llama3.2-korean:latest"
class Colors:
    """ANSI color codes for terminal formatting."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    # Regular colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

class KoreanAdventure:
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = MODEL # preferred model
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
        
        # Direction symbols for better UI
        self.direction_symbols = {
            "north": "↑",
            "south": "↓",
            "east": "→",
            "west": "←",
            "up": "⤴",
            "down": "⤵",
            "northeast": "↗",
            "northwest": "↖",
            "southeast": "↘",
            "southwest": "↙"
        }

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def generate_game_world(self):
        """Generate the initial game world using the LLM."""
        prompt = """
        Create a cozy, magical text adventure game world for Korean language learning. Design it for absolute beginners.
        
        The world should have 4-5 interconnected rooms that form a small, coherent adventure with a simple goal.
        
        Each room should have:
        1. A Korean name (with English translation in parentheses)
        2. A short atmospheric description that incorporates exactly ONE Korean vocabulary word (marked with <KOREAN>)
        3. Available exits (directions to other rooms)
        4. 1-2 items that can be picked up
        5. One character to talk to who will teach a Korean word
        
        Each item should have:
        1. A description that includes a Korean word (marked with <KOREAN>)
        2. A simple use case that helps the player progress
        
        Each character should:
        1. Have a brief description
        2. Offer dialogue that teaches exactly ONE Korean word (marked with <KOREAN>)
        3. Optionally provide a hint about the game's objective
        
        The game should have a simple objective like:
        - Find a special item
        - Help a character by bringing them something
        - Discover a hidden location
        - Learn a specific number of Korean words
        
        Provide the response as valid JSON with this structure:
        {
          "game_title": "Korean title (English translation)",
          "objective": "Brief description of the player's goal",
          "instructions": "2-3 sentences explaining how to play and learn Korean words",
          "rooms": {
            "room_id": {
              "name": "Korean Room Name (English translation)",
              "description_template": "Room description with a <KOREAN> placeholder.",
              "exits": {"north": "other_room_id", "south": "another_room_id", ...},
              "items": ["item1", "item2"],
              "characters": ["character1"]
            },
            ...more rooms...
          },
          "items": {
            "item1": {
              "name": "Korean Item Name (English translation)",
              "description": "Description with <KOREAN> placeholder",
              "use_hint": "Hint about how this item might be used"
            },
            ...more items...
          },
          "characters": {
            "character1": {
              "name": "Korean Character Name (English translation)",
              "description": "Description of the character",
              "dialogue_template": "Character dialogue with a <KOREAN> placeholder.",
              "hint": "Optional hint about game objective or using items"
            },
            ...more characters...
          },
          "vocabulary": [
            {"hangul": "한국어", "romanization": "hangugeo", "meaning": "Korean language", "usage_example": "저는 한국어를 공부해요. (I study Korean.)"},
            ...more vocabulary words...
          ]
        }

        The world should be whimsical and magical, designed specifically for language learning.
        Make sure all room exits connect properly (if room A has a north exit to room B, then room B should have a south exit to room A).
        Include vocabulary appropriate for absolute beginners (greetings, simple objects, colors, numbers 1-10, etc.).
        Each Korean word should appear with its romanization and English meaning.
        
        Fixed available actions in the game:
        - Look (examine surroundings or objects)
        - Move (north, south, east, west)
        - Take (pick up items)
        - Drop (discard items)
        - Talk (communicate with NPCs)
        - Use (interact with items)
        - Give (transfer items to others)
        - Inventory (check carried items)
        - Help (view commands/instructions)
        
        Adventure text should be concise, with exactly one vocabulary word per description.
        """

        try:
            response = self.query_llm(prompt)
            world_data = json.loads(response)
            
            # Store game metadata
            self.game_title = world_data.get("game_title", "Korean Adventure")
            self.objective = world_data.get("objective", "Learn Korean words while exploring")
            self.instructions = world_data.get("instructions", "Type 'help' for commands. Korean words will be highlighted.")
            
            # Store world data
            self.rooms = world_data["rooms"]
            self.items = {item_id: item_data for item_id, item_data in world_data.get("items", {}).items()}
            self.characters = world_data["characters"]
            
            # Store vocabulary
            if "vocabulary" in world_data:
                self.korean_words = world_data["vocabulary"]
            
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
        # Initialize starter vocabulary
        self.korean_words = [
            {"hangul": "바람", "romanization": "baram", "meaning": "wind", "usage_example": "바람이 불어요 (The wind blows)"},
            {"hangul": "의자", "romanization": "uija", "meaning": "chair", "usage_example": "의자에 앉아요 (I sit on the chair)"},
            {"hangul": "책", "romanization": "chaek", "meaning": "book", "usage_example": "책을 읽어요 (I read a book)"},
            {"hangul": "문", "romanization": "mun", "meaning": "door", "usage_example": "문을 열어요 (I open the door)"},
            {"hangul": "차", "romanization": "cha", "meaning": "tea", "usage_example": "차를 마셔요 (I drink tea)"},
            {"hangul": "새", "romanization": "sae", "meaning": "bird", "usage_example": "새가 날아요 (The bird flies)"},
            {"hangul": "달", "romanization": "dal", "meaning": "moon", "usage_example": "달이 밝아요 (The moon is bright)"},
            {"hangul": "물", "romanization": "mul", "meaning": "water", "usage_example": "물을 마셔요 (I drink water)"},
            {"hangul": "나무", "romanization": "namu", "meaning": "tree", "usage_example": "나무가 커요 (The tree is big)"},
            {"hangul": "꽃", "romanization": "kkoch", "meaning": "flower", "usage_example": "꽃이 예뻐요 (The flower is pretty)"}
        ]
        
        # Game title and objectives for fallback world
        self.game_title = "마법의 숲 (Magic Forest)"
        self.objective = "Collect the magical items and learn Korean words"
        self.instructions = "Move between rooms, talk to characters, and collect items. Each interaction teaches you a Korean word."
        
        self.rooms = {
            "garden": {
                "name": "정원 (Garden)",
                "description_template": "You stand in a beautiful garden where a gentle <KOREAN> rustles the leaves.",
                "exits": {"north": "cottage", "east": "forest"},
                "items": ["flower"],
                "characters": ["cat"]
            },
            "cottage": {
                "name": "작은 집 (Cottage)",
                "description_template": "A warm cottage with a crackling fire. A comfortable <KOREAN> sits by the window.",
                "exits": {"south": "garden", "east": "library"},
                "items": ["book"],
                "characters": ["old_woman"]
            },
            "forest": {
                "name": "숲 (Forest)",
                "description_template": "Tall trees surround you as a <KOREAN> sings somewhere above.",
                "exits": {"west": "garden", "north": "library"},
                "items": ["mushroom"],
                "characters": ["fox"]
            },
            "library": {
                "name": "도서관 (Library)",
                "description_template": "Shelves of books reach to the ceiling. A magical <KOREAN> glows faintly on a pedestal.",
                "exits": {"west": "cottage", "south": "forest"},
                "items": ["scroll"],
                "characters": ["scholar"]
            }
        }
        
        self.items = {
            "flower": {
                "name": "꽃 (Flower)",
                "description": "A beautiful flower with petals that shimmer in the light. It contains the essence of <KOREAN>.",
                "use_hint": "Perhaps the Old Woman would like this flower?"
            },
            "book": {
                "name": "책 (Book)",
                "description": "A small book with Korean phrases for travelers. The word <KOREAN> is written on the cover.",
                "use_hint": "The Scholar might find this book interesting."
            },
            "mushroom": {
                "name": "버섯 (Mushroom)",
                "description": "A curious blue mushroom that seems to glow slightly. It smells like <KOREAN>.",
                "use_hint": "This mushroom might be useful for making tea."
            },
            "scroll": {
                "name": "두루마리 (Scroll)",
                "description": "An ancient scroll with Korean characters written in gold ink. The word <KOREAN> stands out.",
                "use_hint": "The scroll contains ancient knowledge."
            }
        }
        
        self.characters = {
            "cat": {
                "name": "고양이 (Cat)",
                "description": "A black cat with intelligent eyes watches you curiously.",
                "dialogue_template": "The cat purrs and says, 'Find the <KOREAN> that leads to wisdom.'",
                "hint": "The scroll in the library might be what you seek."
            },
            "old_woman": {
                "name": "할머니 (Grandmother)",
                "description": "An elderly woman rocks gently in her chair.",
                "dialogue_template": "The woman smiles and says, 'Would you like some <KOREAN>, dear traveler?'",
                "hint": "I'd love a pretty flower to brighten up my cottage."
            },
            "fox": {
                "name": "여우 (Fox)",
                "description": "A red fox with unusually bright eyes sits on a tree stump.",
                "dialogue_template": "The fox tilts its head and says, 'The <KOREAN> reveals hidden paths.'",
                "hint": "Mushrooms have magical properties when prepared correctly."
            },
            "scholar": {
                "name": "학자 (Scholar)",
                "description": "A scholarly figure in robes examines an ancient manuscript.",
                "dialogue_template": "The scholar looks up and says, 'Knowledge is like <KOREAN> - it flows freely.'",
                "hint": "I've been looking for a specific book about travel phrases."
            }
        }
        
        self.current_room = "garden"
        self.discovered_words = set()

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

    def display_korean_word(self, korean_word):
        """Format and display a Korean vocabulary word with additional information."""
        print("\n┌─────────── New Korean Word ───────────┐")
        print(f"│  {Colors.BOLD}{korean_word['hangul']}{Colors.RESET}")
        
        if 'romanization' in korean_word:
            print(f"│  Pronunciation: {korean_word['romanization']}")
        
        print(f"│  Meaning: {korean_word['meaning']}")
        
        if 'usage_example' in korean_word:
            print(f"│  Example: {korean_word['usage_example']}")
        
        print("└─────────────────────────────────────────┘")
        self.discovered_words.add(korean_word['hangul'])

    def display_room(self):
        """Display the current room information with improved visual formatting."""
        if self.current_room not in self.rooms:
            print(f"Error: Room '{self.current_room}' not found!")
            return
            
        room = self.rooms[self.current_room]
        
        # Get Korean word for this room
        korean_word = self.get_next_korean_word()
        
        self.clear_screen()
        
        # Title banner with room name
        title = f" {room['name']} "
        padding = "═" * ((60 - len(title)) // 2)
        print(f"\n{Colors.BRIGHT_CYAN}{padding}{title}{padding}{Colors.RESET}")
        
        # Room description with highlighted Korean word
        description = room["description_template"].replace(
            "<KOREAN>", 
            f"{Colors.YELLOW}{Colors.BOLD}{korean_word['hangul']}{Colors.RESET}"
        )
        print(f"\n{description}\n")
        
        # Display the Korean word information in a styled box
        self.display_korean_word(korean_word)
        
        # Create a visually distinct section for navigation
        print(f"\n{Colors.BRIGHT_BLUE}╔════════ NAVIGATION ════════╗{Colors.RESET}")
        
        # Format exits with direction symbols and colors
        for direction, destination in room["exits"].items():
            symbol = self.direction_symbols.get(direction, "•")
            dest_name = self.rooms[destination]["name"] if destination in self.rooms else destination
            print(f"{Colors.BRIGHT_BLUE}║ {Colors.RESET}{Colors.GREEN}{symbol} {direction}{Colors.RESET} → {dest_name}")
        
        print(f"{Colors.BRIGHT_BLUE}╚═══════════════════════════╝{Colors.RESET}")
        
        # Show items in the room with emoji indicators
        if room.get("items"):
            print(f"\n{Colors.BRIGHT_YELLOW}✨ Items in this area:{Colors.RESET}")
            for item_id in room["items"]:
                if item_id in self.items:
                    print(f"  {Colors.YELLOW}• {self.items[item_id]['name']}{Colors.RESET}")
        
        # Show characters in the room with emoji indicators
        if room.get("characters"):
            print(f"\n{Colors.BRIGHT_MAGENTA}👤 Characters here:{Colors.RESET}")
            for char_id in room["characters"]:
                if char_id in self.characters:
                    print(f"  {Colors.MAGENTA}• {self.characters[char_id]['name']}{Colors.RESET}")
                    
        # Show command prompt with styling
        print(f"\n{Colors.BRIGHT_GREEN}┌─ Enter command{Colors.RESET}")
        print(f"{Colors.BRIGHT_GREEN}└─╼{Colors.RESET} ", end="")

    def handle_command(self, command):
        """Process the player's command."""
        parts = command.lower().split()
        
        if not parts:
            return
            
        action = parts[0]
        
        # Basic directional movement shortcuts
        if action in ["north", "south", "east", "west", "up", "down", "left", "right"]:
            # Map left/right to west/east
            if action == "left": action = "west"
            if action == "right": action = "east"
            self.move_player(action)
            return
            
        # Standard commands
        if action == "look" or action == "examine":
            if len(parts) > 1:
                # Looking at a specific item or character
                target = parts[1]
                self.examine_target(target)
            else:
                # Just redisplay the room
                pass
            
        elif action == "move" or action == "go":
            if len(parts) > 1:
                direction = parts[1]
                self.move_player(direction)
            else:
                print(f"{Colors.YELLOW}Which direction do you want to move?{Colors.RESET}")
                time.sleep(1)
            
        elif action in ["take", "grab", "pick", "get"] and len(parts) > 1:
            item = " ".join(parts[1:]) if len(parts) > 2 else parts[1]
            self.take_item(item)
            
        elif action == "drop" and len(parts) > 1:
            item = " ".join(parts[1:]) if len(parts) > 2 else parts[1]
            self.drop_item(item)
        
        elif action in ["talk", "say", "speak"] and len(parts) > 1:
            character = " ".join(parts[1:]) if len(parts) > 2 else parts[1]
            if action == "say" and "to" in parts:
                # Handle "say hello to character" format
                to_index = parts.index("to")
                character = " ".join(parts[to_index+1:])
            self.talk_to_character(character)
            
        elif action == "use" and len(parts) > 1:
            item = " ".join(parts[1:]) if len(parts) > 2 else parts[1]
            self.use_item(item)
            
        elif action == "give" and len(parts) > 1:
            # Parse "give item to character"
            if "to" in parts:
                to_index = parts.index("to")
                item = " ".join(parts[1:to_index])
                character = " ".join(parts[to_index+1:])
                self.give_item(item, character)
            else:
                print(f"{Colors.YELLOW}Specify who to give the item to. Example: give flower to woman{Colors.RESET}")
                time.sleep(1.5)
            
        elif action in ["open", "unlock"]:
            if len(parts) > 1:
                target = " ".join(parts[1:])
                self.open_target(target)
            else:
                print(f"{Colors.YELLOW}What would you like to open?{Colors.RESET}")
            
        elif action == "close":
            if len(parts) > 1:
                target = " ".join(parts[1:])
                self.close_target(target)
            else:
                print(f"{Colors.YELLOW}What would you like to close?{Colors.RESET}")
            
        elif action == "eat":
            if len(parts) > 1:
                food = " ".join(parts[1:])
                self.consume_item(food, "eat")
            else:
                print(f"{Colors.YELLOW}What would you like to eat?{Colors.RESET}")
            
        elif action == "drink":
            if len(parts) > 1:
                beverage = " ".join(parts[1:])
                self.consume_item(beverage, "drink")
            else:
                print(f"{Colors.YELLOW}What would you like to drink?{Colors.RESET}")
            
        elif action == "inventory" or action == "i" or action == "items":
            self.show_inventory()
            
        elif action == "help" or action == "?":
            self.show_help()
            
        elif action == "exit" or action == "quit":
            self.game_running = False
            print(f"{Colors.BRIGHT_GREEN}Thank you for playing! 안녕히 가세요 (Goodbye)!{Colors.RESET}")
            
        else:
            # Use LLM to understand unusual commands
            self.handle_custom_command(command)

    def handle_custom_command(self, command):
        """Handle custom commands using the LLM for more dynamic gameplay."""
        # More flexible and open-ended prompt that allows creative responses
        prompt = f"""
        In our Korean language learning adventure game, the player has entered: "{command}"
        
        Current situation:
        - The player is in: "{self.rooms[self.current_room]['name']}"
        - Room description: "{self.rooms[self.current_room]['description_template'].replace('<KOREAN>', '[Korean word]')}"
        - Available exits: {list(self.rooms[self.current_room]['exits'].keys())}
        - Items in room: {[self.items[i]['name'] for i in self.rooms[self.current_room].get('items', [])]}
        - Characters in room: {[self.characters[c]['name'] for c in self.rooms[self.current_room].get('characters', [])]}
        - Items in inventory: {[self.items[i]['name'] for i in self.inventory if i in self.items]}
        
        You are a helpful game master, and you can:
        1. Interpret the player's command and translate it to a standard game action
        2. OR provide a direct response if it's a conversation or question
        3. OR create a custom reaction to their unique action
        
        For standard commands, respond in this JSON format:
        {{
          "action_type": "standard",
          "command": "[look/move/take/talk/etc.]",
          "parameters": "[relevant parameters]"
        }}
        
        For conversations, questions, or unique actions, respond in this format:
        {{
          "action_type": "custom",
          "response": "Your creative response that answers the question or reacts to their action",
          "teach_korean": true,
          "korean_word": "{{hangul}}",
          "meaning": "English meaning"
        }}
        
        Include a Korean word in custom responses when appropriate. Make the game fun, responsive and educational!
        
        Return only the JSON, nothing else.
        """
        
        try:
            # Display a shorter loading message for better UX
            print(f"{Colors.BRIGHT_CYAN}Thinking...{Colors.RESET}")
            
            response = self.query_llm(prompt)
            result = json.loads(response)
            
            if result["action_type"] == "standard":
                # Handle standard commands by calling the appropriate method
                if result["command"] == "look":
                    if "parameters" in result and result["parameters"]:
                        self.examine_target(result["parameters"])
                    else:
                        # Will redisplay the room naturally on next loop
                        pass
                elif result["command"] == "move":
                    self.move_player(result["parameters"])
                elif result["command"] == "take":
                    self.take_item(result["parameters"])
                elif result["command"] == "talk":
                    self.talk_to_character(result["parameters"])
                elif result["command"] == "use":
                    self.use_item(result["parameters"])
                elif result["command"] == "give":
                    # Parse parameters (expected format: "item_name to character_name")
                    if "to" in result["parameters"]:
                        parts = result["parameters"].split(" to ")
                        if len(parts) == 2:
                            self.give_item(parts[0], parts[1])
                        else:
                            print("Please specify what to give and to whom.")
                    else:
                        print("Please use format: give [item] to [character]")
                elif result["command"] == "inventory":
                    self.show_inventory()
                elif result["command"] == "help":
                    self.show_help()
                elif result["command"] == "open":
                    self.open_target(result["parameters"])
                elif result["command"] == "close":
                    self.close_target(result["parameters"])
                elif result["command"] == "eat":
                    self.consume_item(result["parameters"], "eat")
                elif result["command"] == "drink":
                    self.consume_item(result["parameters"], "drink")
                else:
                    print(f"I don't understand how to '{result['command']}'. Type 'help' for commands.")
                    
            elif result["action_type"] == "custom":
                # Handle custom responses directly from the LLM
                print("\n" + result["response"])
                
                # If the response includes a Korean word to teach
                if result.get("teach_korean", False) and "korean_word" in result and "meaning" in result:
                    korean_word = {
                        "hangul": result["korean_word"], 
                        "meaning": result["meaning"],
                    }
                    
                    # Add romanization if available
                    if "romanization" in result:
                        korean_word["romanization"] = result["romanization"]
                    
                    # Display the Korean word
                    self.display_korean_word(korean_word)
                    
                    # Add to discovered words
                    self.discovered_words.add(korean_word["hangul"])
                
                input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
                    
        except Exception as e:
            # If JSON parsing fails, the response wasn't properly formatted
            # In this case, just show what the LLM returned directly
            try:
                print("\n" + str(response))
                input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
            except:
                print("I didn't understand that command. Type 'help' for a list of commands.")
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
        
        # Find the item even if the name is a partial match
        matching_items = [i for i in room.get("items", []) if item_name.lower() in i.lower()]
        
        if matching_items:
            item = matching_items[0]
            self.inventory.append(item)
            room["items"].remove(item)
            
            # Get Korean word for this item
            korean_word = self.get_next_korean_word()
            
            print(f"\nYou picked up the {self.items[item]['name']}.")
            
            # Replace placeholder with Korean word
            if item in self.items:
                description = self.items[item]["description"].replace("<KOREAN>", f"{Colors.BOLD}{korean_word['hangul']}{Colors.RESET}")
                print(description)
                
                if "use_hint" in self.items[item]:
                    print(f"\nHint: {self.items[item]['use_hint']}")
                
                # Display the Korean word information
                self.display_korean_word(korean_word)
            
            input("\nPress Enter to continue...")
        else:
            print(f"\nThere's no {item_name} here.")
            time.sleep(1.5)

    def talk_to_character(self, character_name):
        """Talk to a character in the room."""
        room = self.rooms[self.current_room]
        
        # Find the character even if name is partial match
        matching_chars = []
        for char_id in room.get("characters", []):
            char = self.characters[char_id]
            if character_name.lower() in char_id.lower() or character_name.lower() in char["name"].lower():
                matching_chars.append(char_id)
        
        if matching_chars:
            character_id = matching_chars[0]
            character = self.characters[character_id]
            
            # Get Korean word for this dialogue
            korean_word = self.get_next_korean_word()
            
            print(f"\n【 {character['name']} 】")
            # Replace placeholder with Korean word
            dialogue = character["dialogue_template"].replace("<KOREAN>", f"{Colors.BOLD}{korean_word['hangul']}{Colors.RESET}")
            
            print(f"{dialogue}")
            
            # Show character hint if available
            if "hint" in character and character["hint"]:
                print(f"\n{character['name']} adds: \"{character['hint']}\"")
            
            # Display the Korean word information
            self.display_korean_word(korean_word)
            
            input("\nPress Enter to continue...")
        else:
            print(f"\nThere's no '{character_name}' here to talk to.")
            print(f"Characters in this room: {', '.join([self.characters[c]['name'] for c in room.get('characters', [])])}")
            time.sleep(1.5)

    def show_inventory(self):
        """Display the player's inventory with colorful formatting."""
        self.clear_screen()
        
        # Title with fancy border
        print(f"\n{Colors.BRIGHT_YELLOW}╔═══════════════ INVENTORY ════════════════╗{Colors.RESET}")
        
        if not self.inventory:
            print(f"{Colors.BRIGHT_YELLOW}║{Colors.RESET} Your bag is empty.")
        else:
            for item_id in self.inventory:
                if item_id in self.items:
                    item = self.items[item_id]
                    print(f"{Colors.BRIGHT_YELLOW}║{Colors.RESET} {Colors.YELLOW}✦ {item['name']}{Colors.RESET}")
                    
                    # Show the item's use hint
                    if "use_hint" in item:
                        print(f"{Colors.BRIGHT_YELLOW}║{Colors.RESET}   {Colors.BRIGHT_BLACK}Hint: {item['use_hint']}{Colors.RESET}")
        
        print(f"{Colors.BRIGHT_YELLOW}╠═══════════════════════════════════════════╣{Colors.RESET}")
        
        # Show vocabulary progress with colorful progress bar
        learned_count = len(self.discovered_words)
        total_count = len(self.korean_words)
        progress_percent = int((learned_count / total_count) * 100) if total_count > 0 else 0
        
        # Create a progress bar
        bar_length = 30
        filled_length = int(bar_length * learned_count // total_count)
        bar = f"{Colors.GREEN}{'█' * filled_length}{Colors.BRIGHT_BLACK}{'░' * (bar_length - filled_length)}{Colors.RESET}"
        
        print(f"{Colors.BRIGHT_YELLOW}║{Colors.RESET} {Colors.BRIGHT_CYAN}Korean Words Learned:{Colors.RESET} {learned_count}/{total_count}")
        print(f"{Colors.BRIGHT_YELLOW}║{Colors.RESET} {bar} {progress_percent}%")
        
        print(f"{Colors.BRIGHT_YELLOW}╚═══════════════════════════════════════════╝{Colors.RESET}")
        
        input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")

    def show_help(self):
        """Display the help menu with colorful formatting."""
        self.clear_screen()
        
        # Title with decorative border
        print(f"\n{Colors.BRIGHT_CYAN}╔═══════════════ 도움말 (HELP) ═══════════════╗{Colors.RESET}")
        
        # Command section
        print(f"{Colors.BRIGHT_CYAN}║{Colors.RESET} {Colors.BRIGHT_GREEN}Available Commands:{Colors.RESET}")
        
        commands = [
            ("look", "Look around the current room"),
            (f"move {Colors.YELLOW}[direction]{Colors.RESET}", "Move north, south, east, west"),
            (f"take {Colors.YELLOW}[item]{Colors.RESET}", "Pick up an item"),
            (f"talk {Colors.YELLOW}[character]{Colors.RESET}", "Talk to a character"),
            (f"use {Colors.YELLOW}[item]{Colors.RESET}", "Use an item you're carrying"),
            (f"give {Colors.YELLOW}[item]{Colors.RESET} to {Colors.YELLOW}[character]{Colors.RESET}", "Give an item to character"),
            ("inventory", "Check items and learned words"),
            ("help", "Show this help menu"),
            ("exit", "Quit the game")
        ]
        
        for cmd, desc in commands:
            print(f"{Colors.BRIGHT_CYAN}║{Colors.RESET} {Colors.BRIGHT_WHITE}{cmd:<30}{Colors.RESET} {desc}")
        
        # Korean learning section
        print(f"{Colors.BRIGHT_CYAN}╠═════════════ KOREAN LEARNING ════════════════╣{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}║{Colors.RESET} Each interaction teaches you a new Korean word.")
        print(f"{Colors.BRIGHT_CYAN}║{Colors.RESET} Words are highlighted in {Colors.YELLOW}{Colors.BOLD}yellow{Colors.RESET} and added to your vocabulary.")
        
        # Progress bar for vocabulary
        learned_count = len(self.discovered_words)
        total_count = len(self.korean_words)
        progress_percent = int((learned_count / total_count) * 100) if total_count > 0 else 0
        
        bar_length = 30
        filled_length = int(bar_length * learned_count // total_count)
        bar = f"{Colors.GREEN}{'█' * filled_length}{Colors.BRIGHT_BLACK}{'░' * (bar_length - filled_length)}{Colors.RESET}"
        
        print(f"{Colors.BRIGHT_CYAN}║{Colors.RESET} Words learned: {learned_count}/{total_count}")
        print(f"{Colors.BRIGHT_CYAN}║{Colors.RESET} {bar} {progress_percent}%")
        
        # Game objective section
        print(f"{Colors.BRIGHT_CYAN}╠═════════════ GAME OBJECTIVE ════════════════╣{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}║{Colors.RESET} {self.objective}")
        print(f"{Colors.BRIGHT_CYAN}╚═══════════════════════════════════════════════╝{Colors.RESET}")
        
        input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")

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
        if (success):
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
            print("🤔 Thinking... (this might take a minute the first time)")
            print("Please wait while the AI generates a response...")
            
            # Loading animation
            import sys, time, threading
            
            # Start a simple loading animation in a separate thread
            stop_animation = threading.Event()
            def animate():
                chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
                i = 0
                while not stop_animation.is_set():
                    sys.stdout.write('\r' + "Loading " + chars[i % len(chars)])
                    sys.stdout.flush()
                    time.sleep(0.1)
                    i += 1
            
            animation = threading.Thread(target=animate)
            animation.daemon = True
            animation.start()
            
            # Make the request with no timeout
            response = requests.post(f"{self.ollama_url}/api/generate", json=data)
            
            # Stop the animation
            stop_animation.set()
            animation.join()
            sys.stdout.write('\r' + ' ' * 20 + '\r')  # Clear the loading line
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                print(f"\nError: Ollama API returned status code {response.status_code}")
                return None
        except Exception as e:
            print(f"\nError communicating with Ollama: {e}")
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

    def examine_target(self, target_name):
        """Examine an item, character, or feature in the room."""
        room = self.rooms[self.current_room]
        
        # Check if it's an item in the room
        matching_room_items = [i for i in room.get("items", []) if target_name.lower() in i.lower()]
        if matching_room_items:
            item_id = matching_room_items[0]
            item = self.items[item_id]
            
            # Get Korean word for this examination
            korean_word = self.get_next_korean_word()
            
            print(f"\n{Colors.YELLOW}【 {item['name']} 】{Colors.RESET}")
            description = item["description"].replace("<KOREAN>", f"{Colors.YELLOW}{Colors.BOLD}{korean_word['hangul']}{Colors.RESET}")
            print(description)
            
            # Display the Korean word information
            self.display_korean_word(korean_word)
            
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
            return
        
        # Check if it's an item in inventory
        matching_inventory = [i for i in self.inventory if target_name.lower() in i.lower()]
        if matching_inventory:
            item_id = matching_inventory[0]
            item = self.items[item_id]
            
            print(f"\n{Colors.YELLOW}【 {item['name']} 】{Colors.RESET}")
            print(f"{item['description'].replace('<KOREAN>', '')}")
            
            if "use_hint" in item:
                print(f"\nHint: {item['use_hint']}")
                
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
            return
        
        # Check if it's a character
        for char_id in room.get("characters", []):
            char = self.characters[char_id]
            if target_name.lower() in char_id.lower() or target_name.lower() in char["name"].lower():
                print(f"\n{Colors.MAGENTA}【 {char['name']} 】{Colors.RESET}")
                print(char["description"])
                print(f"\nYou can talk to this character by typing: talk {char_id}")
                
                input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
                return
        
        # If nothing matched
        print(f"\nYou don't see any '{target_name}' here to examine.")
        time.sleep(1.5)

    def drop_item(self, item_name):
        """Drop an item from the inventory into the current room."""
        # Find the item in inventory
        matching_items = [i for i in self.inventory if item_name.lower() in i.lower() or 
                         (i in self.items and item_name.lower() in self.items[i]["name"].lower())]
        
        if matching_items:
            item_id = matching_items[0]
            
            # Add to room
            room = self.rooms[self.current_room]
            if "items" not in room:
                room["items"] = []
            room["items"].append(item_id)
            
            # Remove from inventory
            self.inventory.remove(item_id)
            
            print(f"\nYou dropped the {self.items[item_id]['name']}.")
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
        else:
            print(f"\nYou don't have a '{item_name}' to drop.")
            time.sleep(1.5)

    def use_item(self, item_name):
        """Use an item from the inventory."""
        # Find the item in inventory
        matching_items = [i for i in self.inventory if item_name.lower() in i.lower() or 
                         (i in self.items and item_name.lower() in self.items[i]["name"].lower())]
        
        if matching_items:
            item_id = matching_items[0]
            item = self.items[item_id]
            
            # Get Korean word for this usage
            korean_word = self.get_next_korean_word()
            
            # General response for using items
            print(f"\nYou use the {item['name']}...")
            
            # Create a custom response using the LLM
            prompt = f"""
            In our Korean learning adventure game, the player is using the '{item['name']}' item.
            
            Create a brief, interesting description of what happens when they use this item.
            Incorporate the Korean word '{korean_word['hangul']}' ({korean_word['meaning']}) into the description.
            
            Keep it concise (1-3 sentences) and magical/whimsical in tone.
            """
            
            try:
                response = self.query_llm(prompt)
                print(response)
                
                # Display the Korean word information
                self.display_korean_word(korean_word)
                
            except Exception as e:
                # Fallback response if LLM fails
                print(f"You use the {item['name']} and notice the word {korean_word['hangul']} glowing on it briefly.")
                print(f"You've learned a new Korean word!")
                
                # Display the Korean word information
                self.display_korean_word(korean_word)
            
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
        else:
            print(f"\nYou don't have a '{item_name}' to use.")
            time.sleep(1.5)

    def give_item(self, item_name, character_name):
        """Give an item to a character."""
        # Check if the item is in inventory
        matching_items = [i for i in self.inventory if item_name.lower() in i.lower() or 
                         (i in self.items and item_name.lower() in self.items[i]["name"].lower())]
        
        if not matching_items:
            print(f"\nYou don't have a '{item_name}' to give.")
            time.sleep(1.5)
            return
            
        item_id = matching_items[0]
        
        # Check if the character is in the room
        room = self.rooms[self.current_room]
        matching_chars = []
        for char_id in room.get("characters", []):
            char = self.characters[char_id]
            if character_name.lower() in char_id.lower() or character_name.lower() in char["name"].lower():
                matching_chars.append(char_id)
        
        if not matching_chars:
            print(f"\nThere's no '{character_name}' here to give anything to.")
            time.sleep(1.5)
            return
            
        char_id = matching_chars[0]
        character = self.characters[char_id]
        
        # Get Korean word for this interaction
        korean_word = self.get_next_korean_word()
        
        # Create a custom response using the LLM
        prompt = f"""
        In our Korean learning adventure game, the player is giving the '{self.items[item_id]['name']}' 
        to character '{character['name']}'.
        
        Create a brief, interesting description of the character's reaction.
        Incorporate the Korean word '{korean_word['hangul']}' ({korean_word['meaning']}) into the dialogue.
        
        Keep it concise (2-3 sentences) and magical/whimsical in tone.
        """
        
        try:
            # Remove from inventory
            self.inventory.remove(item_id)
            
            print(f"\nYou give the {self.items[item_id]['name']} to {character['name']}.")
            
            response = self.query_llm(prompt)
            print(response)
            
            # Display the Korean word information
            self.display_korean_word(korean_word)
            
        except Exception as e:
            # Fallback response if LLM fails
            print(f"\nYou give the {self.items[item_id]['name']} to {character['name']}.")
            print(f"{character['name']} smiles and thanks you, mentioning the word '{korean_word['hangul']}'.")
            print("You've learned a new Korean word!")
            
            # Display the Korean word information
            self.display_korean_word(korean_word)
        
        input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")

    def open_target(self, target_name):
        """Open a container or door."""
        # Get Korean word for this interaction
        korean_word = self.get_next_korean_word()
        
        print(f"\nYou try to open the {target_name}...")
        print(f"As you do, you notice the word {Colors.YELLOW}{Colors.BOLD}{korean_word['hangul']}{Colors.RESET} written on it.")
        
        # Display the Korean word information
        self.display_korean_word(korean_word)
        
        # Add logic for actually opening things here, if the game design needs it
        print(f"The {target_name} opens, revealing nothing special inside.")
        
        input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")

    def close_target(self, target_name):
        """Close a container or door."""
        print(f"\nYou close the {target_name}.")
        time.sleep(1.5)

    def consume_item(self, item_name, action_type):
        """Eat or drink an item."""
        # Check if the item is in inventory
        matching_items = [i for i in self.inventory if item_name.lower() in i.lower() or 
                         (i in self.items and item_name.lower() in self.items[i]["name"].lower())]
        
        if matching_items:
            item_id = matching_items[0]
            
            # Get Korean word for this interaction
            korean_word = self.get_next_korean_word()
            
            print(f"\nYou {action_type} the {self.items[item_id]['name']}.")
            print(f"It tastes like {Colors.YELLOW}{Colors.BOLD}{korean_word['hangul']}{Colors.RESET}.")
            
            # Remove from inventory
            self.inventory.remove(item_id)
            
            # Display the Korean word information
            self.display_korean_word(korean_word)
            
            input(f"\n{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
        else:
            print(f"\nYou don't have a '{item_name}' to {action_type}.")
            time.sleep(1.5)

def test_ollama_connection(url="http://localhost:11434", model=MODEL):
    """Test connection to Ollama before starting the game."""
    print("Testing connection to Ollama...")
    try:
        # First attempt with provided URL
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
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Error connecting to Ollama: {e}")
        print("Make sure Ollama is running with the command: ollama serve")
        print(f"And that you have the model '{model}' pulled (run: ollama pull {model})")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        print("Make sure Ollama is running with the command: ollama serve")
        print(f"And that you have the model '{model}' pulled (run: ollama pull {model})")
        return False

def main():
    # Test connection to Ollama
    ollama_url = "http://localhost:11434"  # Default Ollama URL
    model = MODEL  # Default model to match the one used in KoreanAdventure
    
    # Allow custom URL and model from command line arguments
    import sys
    if len(sys.argv) > 1:
        ollama_url = sys.argv[1]
    if len(sys.argv) > 2:
        model = sys.argv[2]
    
    if test_ollama_connection(ollama_url, model):
        game = KoreanAdventure(ollama_url)
        game.run()  # Already uses the model from the class
    else:
        print("\nPlease start Ollama before running this game.")
        print(f"1. Run: ollama serve")
        print(f"2. Pull a model: ollama pull {model}")
        print(f"3. Then try again!")
        
        # Add docker-specific debug info
        print("\nDocker troubleshooting tips:")
        print("- If using Docker, make sure port 11434 is properly mapped")
        print("- Try running with: python dynamic-korean-adventure.py http://localhost:11434")
        print("- Check that your model is properly pulled in the Docker container")

if __name__ == "__main__":
    main()
