#!/usr/bin/env python3
"""
multi.py
🐺 Anthro-friendly deterministic Tarot with reversals and color output.
Enhanced with protection through cryptographic hashing.
Interactive multi-card selection based on hashes.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict
import hashlib
import sys
import random

# ----- Optional color UI via rich ----- 
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# ----- Constants and Configuration ----- 
@dataclass(frozen=True)
class TarotCard:
    """Immutable representation of a Tarot card."""
    name: str
    is_major: bool
    deck_position: int


@dataclass(frozen=True)
class DrawnCard:
    """Represents a drawn card with orientation and hash."""
    card: TarotCard
    is_reversed: bool
    hash_digest: str


class TarotDeck:
    """Manages the 78-card Tarot deck."""
    
    MAJOR_ARCANA = [
        "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
        "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
        "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
        "The Devil", "The Tower", "The Star", "The Moon", "The Sun", 
        "Judgement", "The World"
    ]
    
    SUITS = ["Wands", "Cups", "Swords", "Pentacles"]
    RANKS = ["Ace"] + [str(n) for n in range(2, 11)] + ["Page", "Knight", "Queen", "King"]
    
    def __init__(self):
        self.cards: List[TarotCard] = self._build_deck()
    
    def _build_deck(self) -> List[TarotCard]:
        """Constructs the complete 78-card deck."""
        deck = []
        for i, name in enumerate(self.MAJOR_ARCANA):
            deck.append(TarotCard(name=name, is_major=True, deck_position=i))
        position = len(self.MAJOR_ARCANA)
        for suit in self.SUITS:
            for rank in self.RANKS:
                name = f"{rank} of {suit}"
                deck.append(TarotCard(name=name, is_major=False, deck_position=position))
                position += 1
        return deck
    
    def __len__(self) -> int:
        return len(self.cards)
    
    def __getitem__(self, index: int) -> TarotCard:
        return self.cards[index]


class ProtectiveHasher:
    """Handles cryptographic operations for reading protection."""
    
    PROTECTION_ITERATIONS = 888_888
    HASH_LENGTH = 32
    
    @staticmethod
    def derive_protected_bytes(base_bytes: bytes, salt_bytes: bytes) -> bytes:
        """Derives protected bytes using PBKDF2-HMAC-SHA256."""
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
        """Creates the base seed and its hex representation from a query."""
        seed_string = f"{query}"
        seed_bytes = hashlib.sha256(seed_string.encode("utf-8")).digest()
        seed_hex = seed_bytes.hex()
        return seed_bytes, seed_hex


class TarotReader:
    """Main tarot reading engine with protective hashing."""
    
    def __init__(self):
        self.deck = TarotDeck()
        self.hasher = ProtectiveHasher()
    
    def prepare_interactive_deck(self, query: str) -> Dict[str, DrawnCard]:
        """
        Generates a full set of 78 drawn cards with unique hashes for selection.
        """
        base_seed, _ = self.hasher.create_seed(query)
        
        # Deterministically shuffle the deck
        indices = list(range(len(self.deck)))
        rng = random.Random(base_seed)
        rng.shuffle(indices)
        
        interactive_deck: Dict[str, DrawnCard] = {}
        
        for i, deck_position in enumerate(indices):
            salt = f"card-{i}".encode("utf-8")
            protected_digest = self.hasher.derive_protected_bytes(base_seed, salt)
            
            is_reversed = (protected_digest[-1] & 1) == 1
            hash_hex = protected_digest.hex()
            
            drawn_card = DrawnCard(
                card=self.deck[deck_position],
                is_reversed=is_reversed,
                hash_digest=hash_hex
            )
            # Use a shorter prefix for user interaction
            interactive_deck[hash_hex[:8]] = drawn_card
            
        return interactive_deck


class TarotApp:
    """Main application controller for interactive sessions."""
    
    def __init__(self):
        self.reader = TarotReader()
    
    def display_card(self, card: DrawnCard, choice: str):
        """Displays a single chosen card."""
        orientation = "Reversed" if card.is_reversed else "Upright"
        if RICH_AVAILABLE:
            card_style = "bright_white" if card.card.is_major else "white"
            orient_style = "red" if card.is_reversed else "green"
            console.print(
                f"Choice [yellow]{choice}[/yellow] reveals: "
                f"[{card_style}]{card.card.name}[/{card_style}] - "
                f"[{orient_style}]{orientation}[/{orient_style}]"
            )
        else:
            print(f"Choice {choice} reveals: {card.card.name} - {orientation}")

    def run_interactive(self):
        """Runs the interactive card selection mode."""
        print("Welcome to Anthro Tarot 🐾")
        query = input("Ask your sacred question to generate the deck: ").strip()
        if not query:
            raise ValueError("A question is required for the reading.")
        
        print("\nGenerating your protected deck...")
        interactive_deck = self.reader.prepare_interactive_deck(query)
        available_hashes = list(interactive_deck.keys())
        
        print("The deck is ready. Choose a hash to reveal a card.")
        
        while True:
            print("\nAvailable Hashes:")
            # Display in columns
            cols = 4
            for i in range(0, len(available_hashes), cols):
                print("  ".join(f"[{h}]" for h in available_hashes[i:i+cols]))

            choice = input("\nEnter a hash prefix to choose a card (or 'quit'): ").strip().lower()
            
            if choice == 'quit':
                break
            
            if not choice:
                continue

            matches = [h for h in available_hashes if h.startswith(choice)]
            
            if len(matches) == 1:
                chosen_hash = matches[0]
                card_to_reveal = interactive_deck[chosen_hash]
                self.display_card(card_to_reveal, chosen_hash)
                available_hashes.remove(chosen_hash)
                if not available_hashes:
                    print("\nAll cards have been revealed. The session is complete.")
                    break
            elif len(matches) > 1:
                print(f"Ambiguous choice. Multiple hashes start with '{choice}'. Please be more specific.")
            else:
                print("Invalid choice. Please pick a hash from the list.")

def main():
    """Main entry point."""
    app = TarotApp()
    try:
        app.run_interactive()
    except KeyboardInterrupt:
        print("\n\nReading canceled. Stay cozy, packmate. 🐺")
        sys.exit(0)
    except (ValueError, SystemExit) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
