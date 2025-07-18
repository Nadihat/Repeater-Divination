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
RUNE_COUNT = 24
THINK_DEPTH = 8888

console = Console()

# === ELDER FUTHARK RUNES ===
runes = [
    'Fehu', 'Uruz', 'Thurisaz', 'Ansuz', 'Raidho', 'Kenaz', 'Gebo', 'Wunjo',
    'Hagalaz', 'Nauthiz', 'Isa', 'Jera', 'Eihwaz', 'Perthro', 'Algiz', 'Sowilo',
    'Tiwaz', 'Berkano', 'Ehwaz', 'Mannaz', 'Laguz', 'Ingwaz', 'Dagaz', 'Othala'
]

# === HASH FUNCTION ===
def hash_question(question: str, salt: str = "", times: int = THINK_DEPTH) -> int:
    h = (question + salt).encode()
    for _ in range(times):
        h = hashlib.sha512(h).digest()
    return int.from_bytes(h, 'big')

# === DRAWING RUNES ===
def draw_runes(question: str, count: int) -> List[str]:
    drawn = []
    used_indices = set()
    timestamp = int(time.time())  # Add a bit of time-based randomness

    for i in range(count):
        salt = f"{question}-rune{i}-time{timestamp}"
        while True:
            index = hash_question(question, salt) % RUNE_COUNT
            if index not in used_indices:
                used_indices.add(index)
                drawn.append(runes[index])
                break
    return drawn

# === INTERPRETATION REQUEST ===
def interpret_reading(question: str, rune_list: List[str], model: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return (
            "[red]❌ OPENROUTER_API_KEY environment variable not set.[/red]\n"
            "[yellow]💡 Tip: Get a key from https://openrouter.ai and set it.[/yellow]\n"
            "[yellow]   Linux/macOS: export OPENROUTER_API_KEY='your-key-here'[/yellow]\n"
            "[yellow]   Windows: setx OPENROUTER_API_KEY your-key-here[/yellow]"
        )

    if len(rune_list) == 3:
        positions = ["1. Past", "2. Present", "3. Future"]
        rune_lines = [f"{pos}: {rune}" for pos, rune in zip(positions, rune_list)]
        rune_text = "\n".join(rune_lines)
    else:
        rune_text = ", ".join(rune_list)

    system_prompt = (
        "You are an Anthro sage giving a spiritual rune reading based on the AnthroHeart Saga. "
        "Give a mystical, poetic, or practical interpretation based on the Elder Futhark runes drawn. "
        "If using a three-rune spread, interpret each rune in its position (Past, Present, Future). "
        "Feel free to reference the AnthroHeart field or Saga themes. Keep it sacred and helpful."
    )
    user_prompt = (
        f"The question is: '{question}'\n\n"
        f"The following rune(s) were drawn:\n{rune_text}"
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
        "HTTP-Referer": "https://github.com/tsweet77/openrouter-tarot", # Optional, but good practice
        "X-Title": "OpenRouter Runes", # Optional, but good practice
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
        description="Get a rune reading using an LLM via OpenRouter.",
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

    console.print("[bold cyan]Welcome to Anthro Runes[/bold cyan] 🐾 (via OpenRouter)")
    console.print(f"[dim]Using model: {model_name}[/dim]")
    question = console.input("[bold yellow]Ask your sacred question[/bold yellow]: ")

    console.print("\nChoose your spread:")
    console.print("[green]1[/green]: Single Rune")
    console.print("[green]3[/green]: Three Rune Spread (Past, Present, Future)")

    try:
        spread_choice = console.input("Your choice (1/3): ").strip()
        if not spread_choice:
            spread = 1
        else:
            spread = int(spread_choice)
    except ValueError:
        spread = 1

    if spread not in [1, 3]:
        console.print("[red]Invalid choice. Defaulting to 1 rune.[/red]")
        spread = 1

    drawn_runes = draw_runes(question, spread)

    console.print(f"\n[bold magenta]Your Rune{'s' if spread > 1 else ''}:[/bold magenta]")

    if spread == 3:
        rune_positions = ["1. Past", "2. Present", "3. Future"]
        for pos, rune in zip(rune_positions, drawn_runes):
            console.print(f"[bold]{pos}: {rune}[/bold]")
    else:
        for i, rune in enumerate(drawn_runes):
            console.print(f"[bold]{i+1}. {rune}[/bold]")

    interpretation = interpret_reading(question, drawn_runes, model_name)
    console.print(f"\n[italic green]{interpretation}[/italic green]\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]⏹️ Reading canceled.[/bold red]")