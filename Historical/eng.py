#!/usr/bin/env python3
"""
eng.py
Deterministic English word divination based on cryptographic hashing.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple
import hashlib
import sys
import random
import argparse

# ----- Optional color UI via rich -----
try:
    from rich.console import Console
    from rich.table import Table
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# ----- Constants and Configuration -----
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
    "send", "yellow", "gun", "allow", "print", "dead", "spot", "desert", "suit", "current", "lift", "rose",
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
    "shell", "neck"
]

@dataclass(frozen=True)
class DrawnWord:
    word: str
    hash_digest: str

class ProtectiveHasher:
    PROTECTION_ITERATIONS = 888_888
    HASH_LENGTH = 32

    @staticmethod
    def derive_protected_bytes(base_bytes: bytes, salt_bytes: bytes) -> bytes:
        try:
            return hashlib.pbkdf2_hmac(
                'sha256', base_bytes, salt_bytes,
                ProtectiveHasher.PROTECTION_ITERATIONS,
                dklen=ProtectiveHasher.HASH_LENGTH
            )
        except Exception as e:
            print(f"Warning: Using fallback hashing method: {e}", file=sys.stderr)
            result = base_bytes
            for _ in range(ProtectiveHasher.PROTECTION_ITERATIONS):
                result = hashlib.sha256(result + salt_bytes).digest()
            return result[:ProtectiveHasher.HASH_LENGTH]

    @staticmethod
    def create_seed(query: str) -> Tuple[bytes, str]:
        seed_bytes = hashlib.sha256(query.encode("utf-8")).digest()
        seed_hex = seed_bytes.hex()
        return seed_bytes, seed_hex

class WordDiviner:
    def __init__(self):
        self.words = WORD_LIST
        self.hasher = ProtectiveHasher()

    def prepare_interactive_words(self, query: str) -> Dict[str, DrawnWord]:
        base_seed, _ = self.hasher.create_seed(query)
        rng = random.Random(base_seed)

        word_indices = list(range(len(self.words)))
        rng.shuffle(word_indices)

        interactive_words: Dict[str, DrawnWord] = {}
        total_hashes = len(word_indices)

        for i, word_index in enumerate(word_indices):
            print(f"Calculating hash {i+1}/{total_hashes}... ", end='\r', file=sys.stderr)
            salt = f"word-{i}".encode("utf-8")
            protected_digest = self.hasher.derive_protected_bytes(base_seed, salt)
            hash_hex = protected_digest.hex()

            drawn_word = DrawnWord(
                word=self.words[word_index],
                hash_digest=hash_hex
            )
            interactive_words[hash_hex[:8]] = drawn_word
        print(file=sys.stderr)

        return interactive_words

class EngApp:
    POSITION_LABELS_3 = ["Past", "Present", "Future"]
    POSITION_LABELS_10 = [
        "Present (Significator)",
        "Challenge (Crossing)",
        "Subconscious (Below)",
        "Recent Past (Behind)",
        "Conscious (Above)",
        "Near Future (Before You)",
        "Self",
        "Environment",
        "Hopes & Fears",
        "Outcome"
    ]

    def __init__(self):
        self.diviner = WordDiviner()

    def display_word(self, drawn_word: DrawnWord, choice: str, index: int, label: str = None):
        label_prefix = f"{label}: " if label else ""
        if RICH_AVAILABLE:
            console.print(
                f"Word #{index+1} ([yellow]{choice}[/yellow]): {label_prefix}[bright_white]{drawn_word.word}[/bright_white]"
            )
        else:
            print(f"Word #{index+1} ({choice}): {label_prefix}{drawn_word.word}")

    def display_overview(self, drawn_words: List[DrawnWord], query: str, num_words: int):
        print("\n--- Reading Overview ---")
        if not drawn_words:
            print("No words were drawn.")
            return

        if RICH_AVAILABLE:
            table = Table(title="Your Word Divination", caption=f'For your query: "{query}"')
            table.add_column("#", justify="right", style="cyan")
            table.add_column("Position", style="cyan")
            table.add_column("Word", style="magenta")

            labels = []
            if num_words == 3:
                labels = self.POSITION_LABELS_3
            elif num_words == 10:
                labels = self.POSITION_LABELS_10

            for i, drawn_word in enumerate(drawn_words):
                label = labels[i] if i < len(labels) else ""
                table.add_row(
                    str(i + 1),
                    label,
                    drawn_word.word,
                )
            console.print(table)
        else:
            print(f'For your query: "{query}" ')
            labels = []
            if num_words == 3:
                labels = self.POSITION_LABELS_3
            elif num_words == 10:
                labels = self.POSITION_LABELS_10

            for i, drawn_word in enumerate(drawn_words):
                label = labels[i] if i < len(labels) else ""
                print(f"{i+1}. {label}: {drawn_word.word}")

    def run_interactive(self):
        print("Welcome to Anthro Word Divination 🐾")
        query = input("Ask your sacred question to generate the words: ").strip()
        if not query:
            raise ValueError("A question is required for the reading.")

        print("\nGenerating your protected word set...")
        interactive_words = self.diviner.prepare_interactive_words(query)
        available_hashes = list(interactive_words.keys())

        while True:
            try:
                num_words_str = input("How many words to draw? (1, 3, or 10): ").strip()
                num_words = int(num_words_str)
                if num_words not in [1, 3, 10]:
                    raise ValueError
                break
            except ValueError:
                print("Invalid input. Please enter 1, 3, or 10.")

        print(f"\nThe word set is ready. Choose {num_words} hashes to reveal your words.")
        print("\nAvailable Hashes:")
        cols = 4
        for i in range(0, len(available_hashes), cols):
            print("  ".join(f"[{h}]" for h in available_hashes[i:i + cols]))

        while True:
            choices_str = input(f"\nEnter {num_words} hash prefixes (3+ chars), separated by commas: ").strip()
            choices = [c.strip().lower() for c in choices_str.split(',') if c.strip()]
            
            if len(choices) != num_words:
                print(f"Please enter exactly {num_words} comma-separated hashes.")
                continue

            invalid_choices = [c for c in choices if len(c) < 3]
            if invalid_choices:
                print("Error: All hash prefixes must be at least 3 characters long.")
                print(f"Invalid prefixes: {', '.join(invalid_choices)}")
                continue
            
            break

        drawn_words: List[DrawnWord] = []
        print("\n--- Your Revealed Words ---")
        for i, choice in enumerate(choices):
            matches = [h for h in available_hashes if h.startswith(choice)]
            if len(matches) == 1:
                chosen_hash = matches[0]
                word_to_reveal = interactive_words[chosen_hash]
                label = None
                if num_words == 3:
                    label = self.POSITION_LABELS_3[i]
                elif num_words == 10:
                    label = self.POSITION_LABELS_10[i]
                self.display_word(word_to_reveal, chosen_hash, i, label)
                drawn_words.append(word_to_reveal)
                available_hashes.remove(chosen_hash)
            elif len(matches) > 1:
                print(f"Word #{i+1}: Ambiguous choice '{choice}'. Multiple hashes match. Reading cannot continue.")
                return
            else:
                print(f"Word #{i+1}: Invalid choice '{choice}'. No matching hash found. Reading cannot continue.")
                return

        self.display_overview(drawn_words, query, num_words)

def main():
    parser = argparse.ArgumentParser(
        description="Deterministic English word divination.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    # No arguments needed for this version, but keeping the structure.
    args = parser.parse_args()

    app = EngApp()
    try:
        app.run_interactive()
    except KeyboardInterrupt:
        print("\n\nReading canceled.")
        sys.exit(0)
    except (ValueError, SystemExit) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
