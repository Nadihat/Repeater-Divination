import hashlib
import requests
import time
import os
import argparse
from typing import List
from rich import print
from rich.console import Console

# === CONFIGURATION ===
# The model can be specified via command-line argument.
# See a list of models at https://openrouter.ai/models
DEFAULT_MODEL = "x-ai/grok-3-beta"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DECK_SIZE = 36
THINK_DEPTH = 8888

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

# === DRAWING CARDS ===
def draw_cards(question: str, count: int) -> List[str]:
    drawn = []
    used_indices = set()
    timestamp = int(time.time())  # Add a bit of time-based randomness

    for i in range(count):
        salt = f"{question}-card{i}-time{timestamp}"
        while True:
            index = hash_question(question, salt) % DECK_SIZE
            if index not in used_indices:
                used_indices.add(index)
                drawn.append(cards[index])
                break
    return drawn

# === INTERPRETATION REQUEST ===
def interpret_reading(question: str, card_list: List[str], model: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return (
            "[red]❌ OPENROUTER_API_KEY environment variable not set.[/red]\n"
            "[yellow]💡 Tip: Get a key from https://openrouter.ai and set it.[/yellow]\n"
            "[yellow]   Linux/macOS: export OPENROUTER_API_KEY='your-key-here'[/yellow]\n"
            "[yellow]   Windows: setx OPENROUTER_API_KEY your-key-here[/yellow]"
        )

    if len(card_list) == 9:
        # 3x3 spread
        card_text = (
            f"1. {card_list[0]} (Past)\n"
            f"2. {card_list[1]} (Present)\n"
            f"3. {card_list[2]} (Future)\n"
            f"4. {card_list[3]} (Reason)\n"
            f"5. {card_list[4]} (Querent)\n"
            f"6. {card_list[5]} (Near Future)\n"
            f"7. {card_list[6]} (Hopes/Fears)\n"
            f"8. {card_list[7]} (Environment)\n"
            f"9. {card_list[8]} (Outcome)"
        )
    else:
        card_text = ", ".join(card_list)

    system_prompt = (
        "You are an Anthro sage giving a spiritual Lenormand reading based on the AnthroHeart Saga. "
        "Give a mystical, poetic, or practical interpretation depending on the tone of the cards. "
        "If using a 9-card spread, interpret each card in its position. "
        "Feel free to reference the AnthroHeart field or Saga themes. Keep it sacred and helpful."
    )
    user_prompt = (
        f"The question is: '{question}'\n\n"
        f"The following Lenormand card(s) were drawn:\n{card_text}"
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/tsweet77/openrouter-lenormand", # Optional, but good practice
        "X-Title": "OpenRouter Lenormand", # Optional, but good practice
    }


    console.print("\n[bold blue]Consulting the digital ether...[/bold blue]")

    try:
        console.print("\n[bold blue]Sending request to OpenRouter...[/bold blue]")
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=300)
        console.print("[bold blue]Received response from OpenRouter.[/bold blue]")
        response.raise_for_status()  # Will raise an exception for 4XX/5XX status codes
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "No response from LLM.")
    except requests.exceptions.HTTPError as e:
        return f"[red]An HTTP error occurred with the OpenRouter API:[/red] {e.response.text}"
    except requests.exceptions.ConnectionError:
        return "[red]❌ Unable to connect to OpenRouter. Check your internet connection.[/red]"
    except Exception as e:
        return f"[red]An unexpected error occurred:[/red] {e}"

# === MAIN LOGIC ===
def main():
    parser = argparse.ArgumentParser(
        description="Get a Lenormand reading using an LLM via OpenRouter.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"The model to use from OpenRouter.\nExample: 'mistralai/mistral-7b-instruct'\nDefault: '{DEFAULT_MODEL}'"
    )
    args = parser.parse_args()
    model_name = args.model

    console.print("[bold cyan]Welcome to Anthro Lenormand[/bold cyan] 🐾 (via OpenRouter)")
    console.print(f"[dim]Using model: {model_name}[/dim]")
    question = console.input("[bold yellow]Ask your sacred question[/bold yellow]: ")

    console.print("\nChoose your spread:")
    console.print("[green]1[/green]: Single Card")
    console.print("[green]3[/green]: Three Card Spread (Past, Present, Future)")
    console.print("[green]9[/green]: Nine Card Spread (3x3)")

    try:
        spread_choice = console.input("Your choice (1/3/9): ").strip()
        if not spread_choice:
            spread = 1
        else:
            spread = int(spread_choice)
    except ValueError:
        spread = 1

    if spread not in [1, 3, 9]:
        console.print("[red]Invalid choice. Defaulting to 1 card.[/red]")
        spread = 1

    drawn_cards = draw_cards(question, spread)

    console.print(f"\n[bold magenta]Your Card{'s' if spread > 1 else ''}:[/bold magenta]")

    if spread == 9:
        positions = [
            "1. Past", "2. Present", "3. Future",
            "4. Reason", "5. Querent", "6. Near Future",
            "7. Hopes/Fears", "8. Environment", "9. Outcome"
        ]
        for pos, card in zip(positions, drawn_cards):
            console.print(f"[bold]{pos}: {card}[/bold]")
    else:
        for i, card in enumerate(drawn_cards):
            console.print(f"[bold]{i+1}. {card}[/bold]")

    interpretation = interpret_reading(question, drawn_cards, model_name)
    console.print(f"\n[italic green]{interpretation}[/italic green]\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]⏹️ Reading canceled.[/bold red]")
