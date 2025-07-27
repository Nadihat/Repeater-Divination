import hashlib
import time
from typing import List
from rich import print
from rich.console import Console

# === CONFIGURATION ===
DECK_SIZE = 36
THINK_DEPTH = 8888
TABLEAU_ROWS = 4
TABLEAU_COLS = 9

console = Console()

# === LENORMAND CARD LIST ===
cards = [
    'Rider', 'Clover', 'Ship', 'House', 'Tree', 'Clouds', 'Snake', 'Coffin', 'Bouquet', 'Scythe', 'Whip', 'Birds',
    'Child', 'Fox', 'Bear', 'Stars', 'Stork', 'Dog', 'Tower', 'Garden', 'Mountain', 'Crossroads', 'Mice', 'Heart',
    'Ring', 'Book', 'Letter', 'Man', 'Woman', 'Lilies', 'Sun', 'Moon', 'Key', 'Fish', 'Anchor', 'Cross'
]

# === HASH FUNCTION ===
def hash_question(question: str, salt: str = "", times: int = THINK_DEPTH) -> int:
    h = (question + salt).encode()
    for _ in range(times):
        h = hashlib.sha512(h).digest()
    return int.from_bytes(h, 'big')

# === SHUFFLE ALL CARDS FOR THE TABLEAU ===
def shuffle_deck(question: str) -> List[str]:
    """
    Performs a time-sensitive deterministic shuffle based on the hash of the question.
    The same question asked at different times will produce a different shuffle.
    """
    shuffled_deck = list(cards)
    timestamp = int(time.time())
    
    # Perform a deterministic Fisher-Yates shuffle seeded by the hash
    for i in range(DECK_SIZE - 1, 0, -1):
        salt = f"{question}-shuffle{i}-time{timestamp}"
        j = hash_question(question, salt) % (i + 1)
        shuffled_deck[i], shuffled_deck[j] = shuffled_deck[j], shuffled_deck[i]
        
    return shuffled_deck

# === DISPLAY TABLEAU ===
def display_tableau(deck: List[str]):
    console.print("\n[bold magenta]Your Grand Tableau:[/bold magenta]")
    for i in range(TABLEAU_ROWS):
        row_start = i * TABLEAU_COLS
        row_end = row_start + TABLEAU_COLS
        row_cards = deck[row_start:row_end]
        
        # Display row number
        print(f"\n[bold cyan]Row {i+1}:[/bold cyan]")
        
        # Display cards in the row with their position
        for j, card in enumerate(row_cards):
            position = row_start + j + 1
            print(f"[green]{position:02d}.[/green] {card}", end="  |  ")
        print() # Newline at the end of the row

# === MAIN LOGIC ===
def main():
    console.print("[bold cyan]Welcome to the Lenormand Grand Tableau[/bold cyan]")
    question = console.input("[bold yellow]Ask your sacred question for the Tableau[/bold yellow]: ")

    if not question.strip():
        console.print("[red]A question is required to generate the Tableau.[/red]")
        return

    shuffled_deck = shuffle_deck(question)
    display_tableau(shuffled_deck)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]⏹️ Reading canceled.[/bold red]")
