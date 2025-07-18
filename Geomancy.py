import hashlib
import requests
import time
import os
import argparse
from typing import List, Tuple
from rich import print
from rich.console import Console
import random

# === CONFIGURATION ===
# The model can be specified via command-line argument.
# See a list of models at https://openrouter.ai/models
DEFAULT_MODEL = "x-ai/grok-3-beta"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
THINK_DEPTH = 8888

console = Console()

# === GEOMANTIC FIGURES ===
figures = {
    (1, 1, 1, 1): "Via (The Way)",
    (1, 1, 1, 2): "Cauda Draconis (The Tail of the Dragon)",
    (1, 1, 2, 1): "Puer (The Boy)",
    (1, 1, 2, 2): "Fortuna Minor (The Lesser Fortune)",
    (1, 2, 1, 1): "Puella (The Girl)",
    (1, 2, 1, 2): "Amissio (Loss)",
    (1, 2, 2, 1): "Carcer (The Prison)",
    (1, 2, 2, 2): "Laetitia (Joy)",
    (2, 1, 1, 1): "Caput Draconis (The Head of the Dragon)",
    (2, 1, 1, 2): "Conjunctio (The Conjunction)",
    (2, 1, 2, 1): "Acquisitio (Gain)",
    (2, 1, 2, 2): "Rubeus (Red)",
    (2, 2, 1, 1): "Fortuna Major (The Greater Fortune)",
    (2, 2, 1, 2): "Albus (White)",
    (2, 2, 2, 1): "Tristitia (Sorrow)",
    (2, 2, 2, 2): "Populus (The People)"
}

# === HASH FUNCTION ===
def hash_question(question: str, salt: str = "", times: int = THINK_DEPTH) -> int:
    h = (question + salt).encode()
    for _ in range(times):
        h = hashlib.sha512(h).digest()
    return int.from_bytes(h, 'big')

# === GEOMANCY SHIELD CHART GENERATION ===
def generate_mothers(question: str) -> List[Tuple[int, int, int, int]]:
    mothers = []
    seed = hash_question(question)
    random.seed(seed)
    for i in range(4):
        lines = [random.choice([1, 2]) for _ in range(4)]
        mothers.append(tuple(lines))
    return mothers

def derive_daughters(mothers: List[Tuple[int, int, int, int]]) -> List[Tuple[int, int, int, int]]:
    daughters = []
    for i in range(4):
        daughter = (mothers[0][i], mothers[1][i], mothers[2][i], mothers[3][i])
        daughters.append(daughter)
    return daughters

def add_figures(fig1: Tuple[int, int, int, int], fig2: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    return tuple([(l1 + l2) % 2 + 1 for l1, l2 in zip(fig1, fig2)])

def generate_shield_chart(question: str) -> dict:
    mothers = generate_mothers(question)
    daughters = derive_daughters(mothers)
    
    nieces = [
        add_figures(mothers[0], mothers[1]),
        add_figures(mothers[2], mothers[3]),
        add_figures(daughters[0], daughters[1]),
        add_figures(daughters[2], daughters[3])
    ]
    
    witnesses = [
        add_figures(nieces[0], nieces[1]),
        add_figures(nieces[2], nieces[3])
    ]
    
    judge = add_figures(witnesses[0], witnesses[1])
    
    chart = {
        "Mothers": [figures[m] for m in mothers],
        "Daughters": [figures[d] for d in daughters],
        "Nieces": [figures[n] for n in nieces],
        "Right Witness": figures[witnesses[0]],
        "Left Witness": figures[witnesses[1]],
        "Judge": figures[judge]
    }
    
    return chart

# === INTERPRETATION REQUEST ===
def interpret_reading(question: str, chart: dict, model: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return (
            "[red]❌ OPENROUTER_API_KEY environment variable not set.[/red]\n"
            "[yellow]💡 Tip: Get a key from https://openrouter.ai and set it.[/yellow]\n"
            "[yellow]   Linux/macOS: export OPENROUTER_API_KEY='your-key-here'[/yellow]\n"
            "[yellow]   Windows: setx OPENROUTER_API_KEY your-key-here[/yellow]"
        )

    chart_text = ""
    for key, value in chart.items():
        if isinstance(value, list):
            chart_text += f"{key}: {', '.join(value)}\n"
        else:
            chart_text += f"{key}: {value}\n"

    system_prompt = (
        "You are an Anthro sage giving a spiritual geomancy reading based on the AnthroHeart Saga. "
        "Give a mystical, poetic, or practical interpretation depending on the tone of the figures. "
        "Interpret the shield chart, paying attention to the roles of the Mothers, Daughters, Nieces, Witnesses, and the Judge. "
        "Feel free to reference the AnthroHeart field or Saga themes. Keep it sacred and helpful."
    )
    user_prompt = (
        f"The question is: '{question}'\n\n"
        f"The following geomantic shield chart was generated:\n{chart_text}"
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
        "X-Title": "OpenRouter Geomancy", # Optional, but good practice
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
        description="Get a geomancy reading using an LLM via OpenRouter.",
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

    console.print("[bold cyan]Welcome to Anthro Geomancy[/bold cyan] 🐾 (via OpenRouter)")
    console.print(f"[dim]Using model: {model_name}[/dim]")
    question = console.input("[bold yellow]Ask your sacred question[/bold yellow]: ")

    chart = generate_shield_chart(question)

    console.print("\n[bold magenta]Your Geomantic Shield Chart:[/bold magenta]")
    for key, value in chart.items():
        if isinstance(value, list):
            console.print(f"[bold]{key}:[/bold] {', '.join(value)}")
        else:
            console.print(f"[bold]{key}:[/bold] {value}")

    interpretation = interpret_reading(question, chart, model_name)
    console.print(f"\n[italic green]{interpretation}[/italic green]\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]⏹️ Reading canceled.[/bold red]")
