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
THINK_DEPTH = 888888

console = Console()

# === TOKI PONA WORD LIST ===
words = [
    'a', 'akesi', 'ala', 'alasa', 'ale', 'ali', 'anpa', 'ante', 'anu', 'awen', 'e', 'en', 'esun', 'ijo', 'ike',
    'ilo', 'insa', 'jaki', 'jan', 'jelo', 'jo', 'kala', 'kalama', 'kama', 'kasi', 'ken', 'kepeken', 'kili',
    'kiwen', 'ko', 'kon', 'kule', 'kulupu', 'kute', 'la', 'lape', 'laso', 'lawa', 'len', 'lete', 'li', 'lili',
    'linja', 'lipu', 'loje', 'lon', 'luka', 'lukin', 'lupa', 'ma', 'mama', 'mani', 'meli', 'mi', 'mije', 'moku',
    'moli', 'monsi', 'mu', 'mun', 'musi', 'mute', 'nanpa', 'nasa', 'nasin', 'nena', 'ni', 'nimi', 'noka', 'o',
    'olin', 'ona', 'open', 'pakala', 'pali', 'palisa', 'pan', 'pana', 'pi', 'pilin', 'pimeja', 'pini', 'pipi',
    'poka', 'poki', 'pona', 'pu', 'sama', 'seli', 'selo', 'seme', 'sewi', 'sijelo', 'sike', 'sin', 'sina',
    'sinpin', 'sitelen', 'sona', 'soweli', 'suli', 'suno', 'supa', 'suwi', 'tan', 'taso', 'tawa', 'telo',
    'tenpo', 'toki', 'tomo', 'tu', 'unpa', 'uta', 'utala', 'walo', 'wan', 'waso', 'wawa', 'weka', 'wile',
    'epiku', 'jasima', 'kijetesantakalu', 'kin', 'kipisi', 'kokosila', 'ku', 'lanpan', 'leko', 'meso',
    'misikeke', 'monsuta', 'n', 'namako', 'oko', 'soko', 'tonsi',
'linluwi', 'majuna', 'nimisin', 'su', 'apeja', 'isipin', 'jami', 'jonke', 'kamalawala', 'kapesi', 'kiki', 'konwe', 'kulijo', 'melome', 'mijomi', 'misa', 'mulapisu', 'nja', 'ojuta', 'oke', 'omekapo', 'owe', 'pake', 'penpo', 'pika', 'po', 'powe', 'puwa', 'san', 'soto', 'sutopatikuna', 'taki', 'te', 'teje', 'to', 'unu', 'usawi', 'wa', 'wasoweli', 'wekama', 'wuwojiti', 'yupekosi'
]
DECK_SIZE = len(words)

# === HASH FUNCTION ===
def hash_question(question: str, salt: str = "", times: int = THINK_DEPTH) -> int:
    h = (question + salt).encode()
    for _ in range(times):
        h = hashlib.sha512(h).digest()
    return int.from_bytes(h, 'big')

# === DRAWING WORDS ===
def draw_words(question: str, count: int) -> List[str]:
    drawn = []
    used_indices = set()
    timestamp = int(time.time())  # Add a bit of time-based randomness

    for i in range(count):
        salt = f"{question}-word{i}-time{timestamp}"
        while True:
            index = hash_question(question, salt) % DECK_SIZE
            if index not in used_indices:
                used_indices.add(index)
                drawn.append(words[index])
                break
    return drawn

# === INTERPRETATION REQUEST ===
def interpret_reading(question: str, word_list: List[str], model: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return (
            "[red]❌ OPENROUTER_API_KEY environment variable not set.[/red]\n"
            "[yellow]💡 Tip: Get a key from https://openrouter.ai and set it.[/yellow]\n"
            "[yellow]   Linux/macOS: export OPENROUTER_API_KEY='your-key-here'[/yellow]\n"
            "[yellow]   Windows: setx OPENROUTER_API_KEY your-key-here[/yellow]"
        )

    word_text = ", ".join(word_list)

    system_prompt = (
        "You are a toki pona expert. Interpret the drawn words in a poetic and insightful way, "
        "connecting them to the user's question. Provide a simple, clear, and helpful message."
    )
    user_prompt = (
        f"The question is: '{question}'\n\n"
        f"The following toki pona word(s) were drawn:\n{word_text}"
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
        "HTTP-Referer": "https://github.com/reden/tcp", 
        "X-Title": "Toki Pona Oracle", 
    }


    console.print("\n[bold blue]Consulting the digital ether...[/bold blue]")

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
        description="Get a toki pona reading using an LLM via OpenRouter.",
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

    console.print("[bold cyan]toki pona oracle[/bold cyan] (via OpenRouter)")
    console.print(f"[dim]Using model: {model_name}[/dim]")
    question = console.input("[bold yellow]Ask your question[/bold yellow]: ")

    try:
        word_count = int(console.input("How many words to draw? (1-10): ").strip())
        if not 1 <= word_count <= 10:
            word_count = 3
    except ValueError:
        word_count = 3

    drawn_words = draw_words(question, word_count)

    console.print(f"\n[bold magenta]Your Word{'s' if word_count > 1 else ''}:[/bold magenta]")
    for i, word in enumerate(drawn_words):
        console.print(f"[bold]{i+1}. {word}[/bold]")

    interpretation = interpret_reading(question, drawn_words, model_name)
    console.print(f"\n[italic green]{interpretation}[/italic green]\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]⏹️ Reading canceled.[/bold red]")
