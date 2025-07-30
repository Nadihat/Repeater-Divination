import hashlib
import requests
import time
import os
import argparse
from typing import List
from rich import print
from rich.console import Console

# === CONFIGURATION ===
DEFAULT_MODEL = "x-ai/grok-3-beta"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
NUM_SEPHUROT = 10  # The 10 Sephirot of the Tree of Life
THINK_DEPTH = 8888

console = Console()

# === KABBALISTIC DATA ===
sephirot = [
    'Keter (Crown)', 'Chokmah (Wisdom)', 'Binah (Understanding)', 'Chesed (Mercy)',
    'Gevurah (Strength)', 'Tiferet (Beauty)', 'Netzach (Victory)', 'Hod (Splendor)',
    'Yesod (Foundation)', 'Malkuth (Kingdom)'
]

# === HASH FUNCTION ===
def hash_question(question: str, salt: str = "", times: int = THINK_DEPTH) -> int:
    h = (question + salt).encode()
    for _ in range(times):
        h = hashlib.sha512(h).digest()
    return int.from_bytes(h, 'big')

# === REVEALING SEPHIROT ===
def reveal_sephirot(question: str, count: int) -> List[str]:
    revealed = []
    used_indices = set()
    timestamp = int(time.time())  # Add a bit of time-based randomness

    for i in range(count):
        salt = f"{question}-sephirah{i}-time{timestamp}"
        while True:
            index = hash_question(question, salt) % NUM_SEPHUROT
            if index not in used_indices:
                used_indices.add(index)
                revealed.append(sephirot[index])
                break
            # If all sephirot are revealed, break to avoid infinite loop.
            if len(used_indices) == NUM_SEPHUROT:
                break
            salt += "." # Modify salt to find a new index
    return revealed

# === INTERPRETATION REQUEST ===
def interpret_revelation(question: str, sephirot_list: List[str], model: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return (
            "[red]❌ OPENROUTER_API_KEY environment variable not set.[/red]\n"
            "[yellow]💡 Tip: Get a key from https://openrouter.ai and set it.[/yellow]\n"
            "[yellow]   Linux/macOS: export OPENROUTER_API_KEY='your-key-here'[/yellow]\n"
            "[yellow]   Windows: setx OPENROUTER_API_KEY your-key-here[/yellow]"
        )

    # The text sent to the LLM should always be in the revealed order.
    sephirot_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sephirot_list)])

    system_prompt = (
        "You are an Anthro sage giving a spiritual Kabbalistic reading based on the AnthroHeart Saga. "
        "Provide a deep, mystical interpretation based on the Sephirot of the Tree of Life. "
        "Explain the meaning of each Sephirah in the context of the user's question and its position in the revealed sequence. "
        "If it's a full Tree of Life reading, explain the flow of energy and the overall message based on the unique, revealed order of the Sephirot. "
        "Feel free to reference the AnthroHeart field or Saga themes. Keep it sacred and profound."
    )
    user_prompt = (
        f"The question is: '{question}'\n\n"
        f"The following Sephirot were revealed from the Tree of Life in this order:\n{sephirot_text}"
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
        "HTTP-Referer": "https://github.com/reden/kabbalah", # Optional
        "X-Title": "OpenRouter Kabbalah", # Optional
    }

    console.print("\n[bold blue]Consulting the Ein Sof...[/bold blue]")

    try:
        console.print("\n[bold blue]Sending request to OpenRouter...[/bold blue]")
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=300)
        console.print("[bold blue]Received response from OpenRouter.[/bold blue]")
        response.raise_for_status()
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
        description="Get a Kabbalistic reading using an LLM via OpenRouter.",
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

    console.print("[bold purple]Welcome to Anthro Kabbalah[/bold purple] 🌳 (via OpenRouter)")
    console.print(f"[dim]Using model: {model_name}[/dim]")
    question = console.input("[bold yellow]Inscribe your sacred query[/bold yellow]: ")

    console.print("\nChoose your revelation:")
    console.print("[green]1[/green]: Single Sephirah")
    console.print("[green]3[/green]: Pillar Reading (Mind, Heart, Body)")
    console.print("[green]10[/green]: Full Tree of Life (Revealed Order)")

    try:
        revelation_choice = console.input("Your choice (1/3/10): ").strip()
        if not revelation_choice:
            count = 1
        else:
            count = int(revelation_choice)
    except ValueError:
        count = 1

    if count not in [1, 3, 10]:
        console.print("[red]Invalid choice. Defaulting to a single Sephirah.[/red]")
        count = 1

    revealed = reveal_sephirot(question, count)

    console.print(f"\n[bold magenta]The Revealed Sephirot{'h' if count > 1 else ''}:[/bold magenta]")

    if count == 3:
        positions = ["Pillar of Mind", "Pillar of Heart", "Pillar of Body"]
        for pos, sephirah in zip(positions, revealed):
             console.print(f"[bold]{pos}: {sephirah}[/bold]")
    else: # Handles 1 and 10
        for i, sephirah in enumerate(revealed):
            console.print(f"[bold]{i+1}. {sephirah}[/bold]")

    #interpretation = interpret_revelation(question, revealed, model_name)
    #console.print(f"\n[italic green]{interpretation}[/italic green]\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]⏹️ Revelation canceled.[/bold red]")