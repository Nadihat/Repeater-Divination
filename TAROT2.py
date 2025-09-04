#!/usr/bin/env python3
"""
TAROT2.py
Automatic, non-deterministic Tarot readings based on cryptographic hashing.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import hashlib
import sys
import argparse
from datetime import datetime, timezone

# ----- Optional color UI via rich ----- 
try:
    from rich.console import Console
    from rich.table import Table
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# ----- Constants and Configuration ----- 
@dataclass(frozen=True)
class TarotCard:
    name: str
    is_major: bool

@dataclass(frozen=True)
class DrawnCard:
    card: TarotCard
    is_reversed: bool

class TarotDeck:
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
        deck = []
        for name in self.MAJOR_ARCANA:
            deck.append(TarotCard(name=name, is_major=True))
        for suit in self.SUITS:
            for rank in self.RANKS:
                name = f"{rank} of {suit}"
                deck.append(TarotCard(name=name, is_major=False))
        return deck

    def __len__(self) -> int:
        return len(self.cards)

# ----- Hashing Engine ----- 
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

def hash_for_int(seed: bytes, salt: str) -> int:
    salt_bytes = salt.encode("utf-8")
    hashed_bytes = ProtectiveHasher.derive_protected_bytes(seed, salt_bytes)
    return int.from_bytes(hashed_bytes, 'big')

# ----- Reading Logic ----- 
class TarotReader:
    POSITION_LABELS = {
        1: ["The Situation"],
        3: ["Past", "Present", "Future"],
        10: [
            "Present (Significator)", "Challenge (Crossing)", "Subconscious (Below)",
            "Recent Past (Behind)", "Conscious (Above)", "Near Future (Before You)",
            "Self", "Environment", "Hopes & Fears", "Outcome"
        ]
    }

    def __init__(self, seed: bytes, reversals_enabled: bool):
        self.deck = TarotDeck()
        self.seed = seed
        self.reversals_enabled = reversals_enabled

    def draw_cards(self, num_cards: int) -> List[DrawnCard]:
        drawn_cards: List[DrawnCard] = []
        available_cards = self.deck.cards.copy()

        for i in range(num_cards):
            if not available_cards:
                break

            # Determine card index
            card_salt = f"card-draw-{i}"
            card_index = hash_for_int(self.seed, card_salt) % len(available_cards)
            card = available_cards.pop(card_index)

            # Determine reversal
            is_reversed = False
            if self.reversals_enabled:
                reversal_salt = f"reversal-{i}"
                # Use the last bit to decide reversal
                is_reversed = (hash_for_int(self.seed, reversal_salt) & 1) == 1
            
            drawn_cards.append(DrawnCard(card=card, is_reversed=is_reversed))
        
        return drawn_cards

    def display_reading(self, drawn_cards: List[DrawnCard], query: str):
        num_cards = len(drawn_cards)
        labels = self.POSITION_LABELS.get(num_cards, [])

        if RICH_AVAILABLE:
            table = Table(title="Your Tarot Reading", caption=f'For your query: "{query}"')
            table.add_column("#", justify="right", style="cyan")
            table.add_column("Position", style="cyan")
            table.add_column("Card", style="magenta")
            table.add_column("Orientation", style="green")

            for i, drawn_card in enumerate(drawn_cards):
                orientation = "Reversed" if drawn_card.is_reversed else "Upright"
                orient_style = "red" if drawn_card.is_reversed else "green"
                label = labels[i] if i < len(labels) else ""
                table.add_row(
                    str(i + 1),
                    label,
                    drawn_card.card.name,
                    f"[{orient_style}]{orientation}[/{orient_style}]"
                )
            console.print(table)
        else:
            print(f'--- Tarot Reading for: "{query}" ---')
            for i, drawn_card in enumerate(drawn_cards):
                orientation = "Reversed" if drawn_card.is_reversed else "Upright"
                label = labels[i] if i < len(labels) else ""
                label_str = f"{label}: " if label else ""
                print(f"{i+1}. {label_str}{drawn_card.card.name} - {orientation}")

# ----- Main Application ----- 
def main():
    parser = argparse.ArgumentParser(
        description="Automatic, non-deterministic Tarot readings.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-q', '--query', required=True, help='Your sacred question for the reading.')
    parser.add_argument(
        '-n', '--num-cards',
        type=int,
        choices=[1, 3, 10],
        default=3,
        help="Number of cards to draw (1, 3, or 10). Default is 3."
    )
    parser.add_argument(
        '-r', '--reversals',
        action='store_true',
        help='Enable card reversals in the reading.'
    )
    args = parser.parse_args()

    # --- Seed Generation --- 
    timestamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
    seed_material = f"{args.query}|{timestamp}".encode('utf-8')
    seed = hashlib.sha256(seed_material).digest()
    
    auth_hash = ProtectiveHasher.derive_protected_bytes(seed, b"tarot-auth")
    auth_string = auth_hash.hex()[:8].upper()

    if RICH_AVAILABLE:
        console.print(f"[bold purple]Tarot Divination for:[/bold purple] '{args.query}'")
        console.print(f"[dim]Time:[/dim] {timestamp}")
        console.print(f"[dim]Auth:[/dim] [bold green]{auth_string}[/bold green]")
        with console.status("[bold cyan]Drawing cards from the ether...[/bold cyan]"):
            reader = TarotReader(seed=seed, reversals_enabled=args.reversals)
            drawn_cards = reader.draw_cards(args.num_cards)
    else:
        print(f"Tarot Divination for: '{args.query}'")
        print(f"Time: {timestamp}")
        print(f"Auth: {auth_string}")
        print("Drawing cards...")
        reader = TarotReader(seed=seed, reversals_enabled=args.reversals)
        drawn_cards = reader.draw_cards(args.num_cards)

    print()
    reader.display_reading(drawn_cards, args.query)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            console.print("[bold red]⏹️ Reading canceled.[/bold red]")
        else:
            print("\nReading canceled.")
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
        else:
            print(f"An unexpected error occurred: {e}")
