#!/usr/bin/env python3
"""
multiv3.py
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
        seed_string = f"{query}"
        seed_bytes = hashlib.sha256(seed_string.encode("utf-8")).digest()
        seed_hex = seed_bytes.hex()
        return seed_bytes, seed_hex


class TarotReader:
    """Main tarot reading engine with protective hashing."""
    def __init__(self):
        self.deck = TarotDeck()
        self.hasher = ProtectiveHasher()

    def prepare_interactive_deck(self, query: str, reversals_enabled: bool) -> Dict[str, DrawnCard]:
        base_seed, _ = self.hasher.create_seed(query)
        rng = random.Random(base_seed)

        # Create a pool of card indices to draw from. Double if reversals are on.
        card_indices = list(range(len(self.deck)))
        if reversals_enabled:
            hash_pool_indices = card_indices * 2
        else:
            hash_pool_indices = card_indices
        rng.shuffle(hash_pool_indices)

        interactive_deck: Dict[str, DrawnCard] = {}
        total_hashes = len(hash_pool_indices)

        for i, deck_position in enumerate(hash_pool_indices):
            print(f"Calculating hash {i+1}/{total_hashes}...", end='\r', file=sys.stderr)
            salt = f"card-{i}".encode("utf-8")
            protected_digest = self.hasher.derive_protected_bytes(base_seed, salt)

            # Reversal is determined by the hash, but only if enabled
            is_reversed = ((protected_digest[-1] & 1) == 1) and reversals_enabled
            hash_hex = protected_digest.hex()

            drawn_card = DrawnCard(
                card=self.deck[deck_position],
                is_reversed=is_reversed,
                hash_digest=hash_hex
            )
            interactive_deck[hash_hex[:8]] = drawn_card
        print(file=sys.stderr)  # Newline after progress indicator

        return interactive_deck


class TarotApp:
    """Main application controller for interactive sessions."""
    def __init__(self, reversals_enabled: bool):
        self.reader = TarotReader()
        self.reversals_enabled = reversals_enabled

    def display_card(self, card: DrawnCard, choice: str, index: int):
        orientation = "Reversed" if card.is_reversed else "Upright"
        if RICH_AVAILABLE:
            card_style = "bright_white" if card.card.is_major else "white"
            orient_style = "red" if card.is_reversed else "green"
            console.print(
                f"Card #{index+1} ([yellow]{choice}[/yellow]): "
                f"[{card_style}]{card.card.name}[/{card_style}] - "
                f"[{orient_style}]{orientation}[/{orient_style}]"
            )
        else:
            print(f"Card #{index+1} ({choice}): {card.card.name} - {orientation}")

    def display_overview(self, drawn_cards: List[DrawnCard]):
        print("\n--- Reading Overview ---")
        if not drawn_cards:
            print("No cards were drawn.")
            return

        if RICH_AVAILABLE:
            table = Table(title="Your Tarot Reading")
            table.add_column("#", justify="right", style="cyan")
            table.add_column("Card", style="magenta")
            table.add_column("Orientation", style="green")

            for i, drawn_card in enumerate(drawn_cards):
                orientation = "Reversed" if drawn_card.is_reversed else "Upright"
                orient_style = "red" if drawn_card.is_reversed else "green"
                table.add_row(
                    str(i + 1),
                    drawn_card.card.name,
                    f"[{orient_style}]{orientation}[/{orient_style}]"
                )
            console.print(table)
        else:
            for i, drawn_card in enumerate(drawn_cards):
                orientation = "Reversed" if drawn_card.is_reversed else "Upright"
                print(f"{i+1}. {drawn_card.card.name} - {orientation}")

    def run_interactive(self):
        print("Welcome to Anthro Tarot 🐾")
        if self.reversals_enabled:
            print("Reversals are ENABLED.")
        query = input("Ask your sacred question to generate the deck: ").strip()
        if not query:
            raise ValueError("A question is required for the reading.")

        print("\nGenerating your protected deck...")
        interactive_deck = self.reader.prepare_interactive_deck(query, self.reversals_enabled)
        available_hashes = list(interactive_deck.keys())

        # Get number of cards
        while True:
            try:
                num_cards_str = input("How many cards to draw? (1, 3, or 10): ").strip()
                num_cards = int(num_cards_str)
                if num_cards not in [1, 3, 10]:
                    raise ValueError
                break
            except ValueError:
                print("Invalid input. Please enter 1, 3, or 10.")

        print(f"\nThe deck is ready. Choose {num_cards} hashes to reveal your cards.")
        print("\nAvailable Hashes:")
        cols = 4
        for i in range(0, len(available_hashes), cols):
            print("  ".join(f"[{h}]" for h in available_hashes[i:i + cols]))

        # Get all choices in one go
        while True:
            choices_str = input(f"\nEnter {num_cards} hash prefixes, separated by commas: ").strip()
            choices = [c.strip().lower() for c in choices_str.split(',') if c.strip()]
            if len(choices) == num_cards:
                break
            else:
                print(f"Please enter exactly {num_cards} comma-separated hashes.")

        drawn_cards: List[DrawnCard] = []
        print("\n--- Your Revealed Cards ---")
        for i, choice in enumerate(choices):
            matches = [h for h in available_hashes if h.startswith(choice)]
            if len(matches) == 1:
                chosen_hash = matches[0]
                card_to_reveal = interactive_deck[chosen_hash]
                self.display_card(card_to_reveal, chosen_hash, i)
                drawn_cards.append(card_to_reveal)
                available_hashes.remove(chosen_hash) # Prevent choosing the same hash twice
            elif len(matches) > 1:
                print(f"Card #{i+1}: Ambiguous choice '{choice}'. Multiple hashes match. Reading cannot continue.")
                return
            else:
                print(f"Card #{i+1}: Invalid choice '{choice}'. No matching hash found. Reading cannot continue.")
                return

        self.display_overview(drawn_cards)


def main():
    parser = argparse.ArgumentParser(
        description="Anthro-friendly deterministic Tarot with reversals and color output.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-r', '--reversals',
        action='store_true',
        help='Enable card reversals, doubling the hash pool.'
    )
    args = parser.parse_args()

    app = TarotApp(reversals_enabled=args.reversals)
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
