#!/usr/bin/env python3

import hashlib
import os
import random
import shutil
import struct
import time
from typing import List

try:
    from rich.console import Console
    from rich.text import Text
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.table import Table
    from rich.align import Align
    from rich.layout import Layout
    from rich.live import Live
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

WORD_LIST = [
    "the", "of", "to", "and", "a", "in", "is", "it", "you", "that", "he", "was", "for", "on", "are", "with", "as",
    "I", "his", "they", "be", "at", "one", "have", "this", "from", "or", "had", "by", "not", "word", "but", "what",
    "some", "we", "can", "out", "other", "were", "all", "there", "when", "up", "use", "your", "how", "said", "an",
    "each", "she", "which", "do", "their", "time", "if", "will", "way", "about", "many", "then", "them", "write",
    "would", "like", "so", "these", "her", "long", "make", "thing", "see", "him", "two", "has", "look", "more",
    "day", "could", "go", "come", "did", "number", "sound", "no", "most", "people", "my", "over", "know", "water",
    "than", "call", "first", "who", "may", "down", "side", "been", "now", "find", "any", "new", "work", "part",
    "take", "get", "place", "made", "live", "where", "after", "back", "little", "only", "round", "man", "year",
    "came", "show", "every", "good", "me", "give", "our", "under", "name", "very", "through", "just", "form",
    "sentence", "great", "think", "say", "help", "low", "line", "differ", "turn", "cause", "much", "mean",
    "before", "move", "right", "boy", "old", "too", "same", "tell", "does", "set", "three", "want", "air", "well",
    "also", "play", "small", "end", "put", "home", "read", "hand", "port", "large", "spell", "add", "even",
    "land", "here", "must", "big", "high", "such", "follow", "act", "why", "ask", "men", "change", "went",
    "light", "kind", "off", "need", "house", "picture", "try", "us", "again", "animal", "point", "mother",
    "world", "near", "build", "self", "earth", "father", "head", "stand", "own", "page", "should", "country",
    "found", "answer", "school", "grow", "study", "still", "learn", "plant", "cover", "food", "sun", "four",
    "between", "state", "keep", "eye", "never", "last", "let", "thought", "city", "tree", "cross", "farm",
    "hard", "start", "might", "story", "saw", "far", "sea", "draw", "left", "late", "run", "don't", "while",
    "press", "close", "night", "real", "life", "few", "north", "open", "seem", "together", "next", "white",
    "children", "begin", "got", "walk", "example", "ease", "paper", "group", "always", "music", "those",
    "both", "mark", "often", "letter", "until", "mile", "river", "car", "feet", "care", "second", "book",
    "carry", "took", "science", "eat", "room", "friend", "began", "idea", "fish", "mountain", "stop", "once",
    "base", "hear", "horse", "cut", "sure", "watch", "color", "face", "wood", "main", "enough", "plain",
    "girl", "usual", "young", "ready", "above", "ever", "red", "list", "though", "feel", "talk", "bird",
    "soon", "body", "dog", "family", "direct", "pose", "leave", "song", "measure", "door", "product", "black",
    "short", "numeral", "class", "wind", "question", "happen", "complete", "ship", "area", "half", "rock",
    "order", "fire", "south", "problem", "piece", "told", "knew", "pass", "since", "top", "whole", "king",
    "space", "heard", "best", "hour", "better", "true", "during", "hundred", "five", "remember", "step",
    "early", "hold", "west", "ground", "interest", "reach", "fast", "verb", "sing", "listen", "six", "table",
    "travel", "less", "morning", "ten", "simple", "several", "vowel", "toward", "war", "lay", "against",
    "pattern", "slow", "center", "love", "person", "money", "serve", "appear", "road", "map", "rain", "rule",
    "govern", "pull", "cold", "notice", "voice", "unit", "power", "town", "fine", "certain", "fly", "fall",
    "lead", "cry", "dark", "machine", "note", "wait", "plan", "figure", "star", "box", "noun", "field",
    "rest", "correct", "able", "pound", "done", "beauty", "drive", "stood", "contain", "front", "teach",
    "week", "final", "gave", "green", "oh", "quick", "develop", "ocean", "warm", "free", "minute", "strong",
    "mind", "behind", "clear", "tail", "produce", "fact", "street", "inch", "multiply", "nothing", "course",
    "stay", "wheel", "full", "force", "blue", "object", "decide", "surface", "deep", "moon", "island", "foot",
    "system", "busy", "test", "record", "boat", "common", "gold", "possible", "plane", "stead", "dry",
    "wonder", "laugh", "thousand", "ago", "ran", "check", "game", "shape", "equate", "hot", "miss", "brought",
    "heat", "snow", "tire", "bring", "yes", "distant", "fill", "east", "paint", "language", "among", "grand",
    "ball", "yet", "wave", "drop", "heart", "am", "present", "heavy", "dance", "engine", "position", "arm",
    "wide", "sail", "material", "size", "vary", "settle", "speak", "weight", "general", "ice", "matter",
    "circle", "pair", "include", "divide", "syllable", "felt", "perhaps", "pick", "sudden", "count", "square",
    "reason", "length", "represent", "art", "subject", "region", "energy", "hunt", "probable", "bed",
    "brother", "egg", "ride", "cell", "believe", "fraction", "forest", "sit", "race", "window", "summer",
    "train", "sleep", "prove", "lone", "leg", "exercise", "wall", "catch", "mount", "wish", "sky", "board",
    "joy", "winter", "sat", "written", "wild", "instrument", "kept", "glass", "grass", "cow", "job", "edge",
    "sign", "visit", "past", "soft", "fun", "bright", "gas", "weather", "month", "million", "bear", "finish",
    "happy", "hope", "flower", "clothe", "strange", "gun", "jump", "baby", "eight", "village", "meet", "root",
    "buy", "raise", "solve", "metal", "whether", "push", "seven", "paragraph", "third", "shall", "held",
    "hair", "describe", "cook", "floor", "either", "result", "burn", "hill", "safe", "cat", "century",
    "consider", "type", "law", "bit", "coast", "copy", "phrase", "silent", "tall", "sand", "soil", "roll",
    "temperature", "finger", "industry", "value", "fight", "lie", "beat", "excite", "natural", "view",
    "sense", "ear", "else", "quite", "broke", "case", "middle", "kill", "son", "lake", "moment", "scale",
    "loud", "spring", "observe", "child", "straight", "consonant", "nation", "dictionary", "milk", "speed",
    "method", "organ", "pay", "age", "section", "dress", "cloud", "surprise", "quiet", "stone", "tiny",
    "climb", "cool", "design", "poor", "lot", "experiment", "bottom", "key", "iron", "single", "stick",
    "flat", "twenty", "skin", "smile", "crease", "hole", "trade", "melody", "trip", "office", "receive",
    "row", "mouth", "exact", "symbol", "die", "least", "trouble", "shout", "except", "wrote", "seed", "tone",
    "join", "suggest", "clean", "lady", "yard", "rise", "bad", "blow", "oil", "blood", "touch", "grew",
    "cent", "mix", "team", "wire", "cost", "lost", "brown", "wear", "garden", "equal", "sent", "choose",
    "fell", "fit", "flow", "fair", "bank", "collect", "control", "decimal", "gentle", "woman", "captain",
    "practice", "separate", "difficult", "doctor", "please", "protect", "noon", "whose", "locate", "ring",
    "character", "insect", "caught", "period", "indicate", "radio", "spoke", "atom", "human", "history",
    "effect", "electric", "expect", "crop", "modern", "element", "hit", "student", "corner", "party",
    "supply", "bone", "rail", "imagine", "provide", "agree", "thus", "capital", "won't", "chair", "danger",
    "fruit", "rich", "thick", "soldier", "process", "operate", "guess", "necessary", "sharp", "wing",
    "create", "neighbor", "wash", "bat", "rather", "crowd", "corn", "compare", "poem", "string", "bell",
    "depend", "meat", "rub", "tube", "famous", "dollar", "stream", "fear", "sight", "thin", "triangle",
    "planet", "hurry", "chief", "colony", "clock", "mine", "tie", "enter", "major", "fresh", "search",
    "send", "yellow", "allow", "print", "dead", "spot", "desert", "suit", "current", "lift", "rose",
    "continue", "block", "chart", "hat", "sell", "success", "company", "subtract", "event", "particular",
    "deal", "swim", "term", "opposite", "wife", "shoe", "shoulder", "spread", "arrange", "camp", "invent",
    "cotton", "born", "determine", "quart", "nine", "truck", "noise", "level", "chance", "gather", "shop",
    "stretch", "throw", "shine", "property", "column", "molecule", "select", "wrong", "gray", "repeat",
    "require", "broad", "salt", "nose", "plural", "anger", "claim", "continent", "oxygen", "sugar", "death",
    "pretty", "skill", "women", "season", "solution", "magnet", "silver", "thank", "branch", "match",
    "suffix", "especially", "fig", "afraid", "huge", "sister", "steel", "discuss", "forward", "similar",
    "guide", "experience", "score", "apple", "bought", "led", "pitch", "coat", "mass", "card", "band",
    "rope", "slip", "win", "dream", "evening", "condition", "feed", "tool", "total", "basic", "smell",
    "valley", "nor", "double", "seat", "arrive", "master", "track", "parent", "shore", "division", "sheet",
    "substance", "favor", "connect", "post", "spend", "chord", "fat", "glad", "original", "share",
    "station", "dad", "bread", "charge", "proper", "bar", "offer", "segment", "slave", "duck", "instant",
    "market", "degree", "populate", "chick", "dear", "enemy", "reply", "drink", "occur", "support",
    "speech", "nature", "range", "steam", "motion", "path", "liquid", "log", "meant", "quotient", "teeth",
    "shell", "neck", "anthro", "cub", "fox", "wolf", "raccoon", "lion", "empty", "beyond", "Disney", "waste"
]

HASH_ROUNDS_SESSION = 8888

class ProtectiveHasher:
    @staticmethod
    def create_seed(query: str) -> bytes:
        """Create a cryptographically secure seed from the query"""
        normalized = query.encode('utf-8')
        entropy = os.urandom(32)
        timing_data = struct.pack('dd', time.time(), time.perf_counter())
        
        payload = entropy + normalized + timing_data
        
        # Multi-round hashing for protection
        current_hash = payload
        for _ in range(HASH_ROUNDS_SESSION):
            current_hash = hashlib.sha256(current_hash).digest()
        
        return current_hash

class DivinationMapper:
    def __init__(self, seed_bytes: bytes):
        # Derive a 32-bit seed from the hash
        first = struct.unpack('>I', seed_bytes[:4])[0]
        last = struct.unpack('>I', seed_bytes[-4:])[0]
        seed = (first ^ last) or 0x9e3779b9
        
        # Create seeded RNG and shuffle word list
        rng = random.Random(seed)
        self.word_map = WORD_LIST.copy()
        rng.shuffle(self.word_map)
    
    def get_word(self, number: int) -> str:
        """Get word for a given number (1-1004)"""
        if 1 <= number <= len(self.word_map):
            return self.word_map[number - 1]
        return "unknown"

class EngWheelApp:
    def __init__(self):
        if RICH_AVAILABLE:
            self.console = Console()
        self.mapper = None
        self.sentence = []
        self.question = ""
        
    def print_colored(self, text: str, color: str = "white", style: str = ""):
        """Print colored text, fallback to plain if rich not available"""
        if RICH_AVAILABLE:
            self.console.print(text, style=f"{style} {color}")
        else:
            print(text)
    
    def display_header(self):
        """Display the application header"""
        if RICH_AVAILABLE:
            title = Text("EngWheel", style="bold magenta")
            subtitle = Text("Enter a question to begin word divination", style="dim cyan")
            panel = Panel(
                Align.center(title + "\n" + subtitle),
                border_style="bright_blue",
                padding=(1, 2)
            )
            self.console.print(panel)
        else:
            print("=" * 50)
            print("                 EngWheel")
            print("      Enter a question to begin word divination")
            print("=" * 50)
    
    def get_question(self) -> str:
        """Get question from user"""
        if RICH_AVAILABLE:
            return Prompt.ask("\n[bold cyan]Enter your question[/bold cyan]", default="")
        else:
            return input("\nEnter your question: ").strip()
    
    def prepare_session(self, question: str):
        """Prepare the divination session"""
        if not question:
            self.print_colored("Please enter a question to begin.", "red")
            return False
        
        self.question = question
        self.print_colored("Preparing session...", "yellow")
        
        seed = ProtectiveHasher.create_seed(question)
        self.mapper = DivinationMapper(seed)
        
        self.print_colored("Session prepared! You can now select numbers.", "green")
        return True
    
    def display_grid_info(self):
        """Display information about the number grid"""
        if RICH_AVAILABLE:
            info_text = Text()
            info_text.append("Grid: ", style="bold")
            info_text.append("Numbers 1-1004 available", style="cyan")
            info_text.append(" | Enter numbers to build your sentence", style="dim")
            self.console.print(info_text)
        else:
            print("\nGrid: Numbers 1-1004 available | Enter numbers to build your sentence")
    
    def display_current_sentence(self):
        """Display the current sentence being built"""
        if not self.sentence:
            return
        
        sentence_text = " ".join(self.sentence)
        if RICH_AVAILABLE:
            panel = Panel(
                Text(sentence_text, style="bold white"),
                title="[bold green]Current Sentence[/bold green]",
                border_style="green"
            )
            self.console.print(panel)
        else:
            print(f"\nCurrent Sentence: {sentence_text}")
    
    def display_number_grid_sample(self):
        """Display a sample of available numbers"""
        if RICH_AVAILABLE:
            table = Table(title="Sample Numbers (1-1004 available)", show_header=False)
            
            # Show first 20 numbers as examples
            for i in range(0, 20, 5):
                row = []
                for j in range(5):
                    num = i + j + 1
                    if num <= 20:
                        word = self.mapper.get_word(num) if self.mapper else "?"
                        row.append(f"[cyan]{num}[/cyan]: [white]{word}[/white]")
                table.add_row(*row)
            
            self.console.print(table)
        else:
            print("\nSample Numbers:")
            for i in range(1, 21):
                word = self.mapper.get_word(i) if self.mapper else "?"
                print(f"{i:3d}: {word}", end="  ")
                if i % 5 == 0:
                    print()
    
    def handle_number_input(self, number_str: str):
        """Handle user number input"""
        try:
            number = int(number_str)
            if not (1 <= number <= 1004):
                self.print_colored("Please enter a number between 1 and 1004.", "red")
                return
            
            if not self.mapper:
                self.print_colored("Please prepare a session first.", "red")
                return
            
            word = self.mapper.get_word(number)
            self.sentence.append(word)
            
            if RICH_AVAILABLE:
                self.console.print(f"[bold blue]{number}[/bold blue] → [bold green]{word}[/bold green]")
            else:
                print(f"{number} → {word}")
            
            self.display_current_sentence()
            
        except ValueError:
            self.print_colored("Please enter a valid number.", "red")
    
    def show_help(self):
        """Show help information"""
        help_text = """
Commands:
  <number>     - Add word for that number (1-1004)
  clear        - Clear current sentence
  restart      - Start over with new question
  help         - Show this help
  quit/exit    - Exit the program
        """
        
        if RICH_AVAILABLE:
            panel = Panel(help_text.strip(), title="[bold yellow]Help[/bold yellow]", border_style="yellow")
            self.console.print(panel)
        else:
            print(help_text)
    
    def run(self):
        """Main application loop"""
        self.display_header()
        
        # Get initial question
        question = self.get_question()
        if not self.prepare_session(question):
            return
        
        self.display_grid_info()
        if self.mapper:
            self.display_number_grid_sample()
        
        self.print_colored("\nEnter numbers to build your sentence, or 'help' for commands:", "cyan")
        
        while True:
            try:
                if RICH_AVAILABLE:
                    user_input = Prompt.ask("[bold]>").strip().lower()
                else:
                    user_input = input("> ").strip().lower()
                
                if user_input in ['quit', 'exit', 'q']:
                    self.print_colored("Goodbye!", "magenta")
                    break
                elif user_input == 'help':
                    self.show_help()
                elif user_input == 'clear':
                    self.sentence = []
                    self.print_colored("Sentence cleared.", "yellow")
                elif user_input == 'restart':
                    self.sentence = []
                    self.mapper = None
                    question = self.get_question()
                    if self.prepare_session(question):
                        self.display_grid_info()
                        self.display_number_grid_sample()
                elif user_input.isdigit():
                    self.handle_number_input(user_input)
                elif user_input:
                    self.print_colored("Unknown command. Type 'help' for available commands.", "red")
                    
            except KeyboardInterrupt:
                self.print_colored("\nGoodbye!", "magenta")
                break
            except EOFError:
                break

def main():
    if not RICH_AVAILABLE:
        print("Note: Install 'rich' package for enhanced colors and formatting:")
        print("pip install rich")
        print()
    
    app = EngWheelApp()
    app.run()

if __name__ == "__main__":
    main()
