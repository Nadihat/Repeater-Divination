import hashlib
import requests
import time
import os
import argparse
from typing import List, Dict, Any
from rich import print
from rich.console import Console

# === CONFIGURATION ===
DEFAULT_MODEL = "x-ai/grok-3-beta"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
THINK_DEPTH = 888888

console = Console()

# === ASTROLOGICAL DATA ===
PLANETS = [
    'Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto'
]
SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]
HOUSES = [
    '1st House', '2nd House', '3rd House', '4th House', '5th House', '6th House',
    '7th House', '8th House', '9th House', '10th House', '11th House', '12th House'
]

# === HASH FUNCTION ===
def hash_question(question: str, salt: str = "", times: int = THINK_DEPTH) -> int:
    h = (question + salt).encode()
    for _ in range(times):
        h = hashlib.sha512(h).digest()
    return int.from_bytes(h, 'big')

# === CHART GENERATION ===
def generate_chart(question: str, count: int) -> List[Dict[str, str]]:
    chart = []
    used_planets = set()
    used_signs = set()
    used_houses = set()
    timestamp = int(time.time())

    # For a 10-placement chart, we use each planet once.
    # For smaller readings, we select planets randomly.
    planets_to_use = PLANETS if count >= 10 else []

    for i in range(count):
        salt = f"{question}-placement{i}-time{timestamp}"
        
        # Select Planet
        while True:
            if count >= 10:
                planet = planets_to_use[i]
            else:
                planet_index = hash_question(question, salt + "planet") % len(PLANETS)
                planet = PLANETS[planet_index]

            if planet not in used_planets:
                used_planets.add(planet)
                break
            salt += "p" # Ensure hash changes to find a new planet

        # Select Sign
        while True:
            sign_index = hash_question(question, salt + "sign") % len(SIGNS)
            sign = SIGNS[sign_index]
            # Allowing duplicate signs for different planets
            break

        # Select House
        while True:
            house_index = hash_question(question, salt + "house") % len(HOUSES)
            house = HOUSES[house_index]
            if house not in used_houses:
                used_houses.add(house)
                break
            salt += "h" # Ensure hash changes to find a new house

        chart.append({"planet": planet, "sign": sign, "house": house})

    return chart

# === INTERPRETATION REQUEST ===
def interpret_chart(question: str, chart: List[Dict[str, str]], model: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return (
            "[red]❌ OPENROUTER_API_KEY environment variable not set.[/red]\n"
            "[yellow]💡 Tip: Get a key from https://openrouter.ai and set it.[/yellow]\n"
            "[yellow]   Linux/macOS: export OPENROUTER_API_KEY='your-key-here'[/yellow]\n"
            "[yellow]   Windows: setx OPENROUTER_API_KEY your-key-here[/yellow]"
        )

    if len(chart) == 10:
        # Using traditional house meanings for positions
        positions = [
            "1. Self, Identity (Ascendant)", "2. Values, Possessions", "3. Communication, Siblings",
            "4. Home, Family, Roots (IC)", "5. Creativity, Romance, Children", "6. Health, Daily Routines",
            "7. Partnerships, Marriage (Descendant)", "8. Transformation, Shared Resources",
            "9. Philosophy, Travel, Higher Ed.", "10. Career, Public Life (Midheaven)"
        ]
        # For a 10-placement chart, we map planets to houses sequentially for interpretation
        chart_lines = [f"{positions[i]}: {placement['planet']} in {placement['sign']}" for i, placement in enumerate(chart)]
        chart_text = "\n".join(chart_lines)
    else:
        chart_text = ", ".join([f"{p['planet']} in {p['sign']} in the {p['house']}" for p in chart])

    system_prompt = (
        "You are an Anthro sage giving a spiritual astrological reading based on the AnthroHeart Saga. "
        "Provide a mystical, poetic, or practical interpretation of the generated astrological chart. "
        "If it's a 10-placement chart, interpret each placement in its corresponding house context. "
        "Feel free to reference the AnthroHeart field or Saga themes. Keep it sacred and insightful."
    )
    user_prompt = (
        f"The question is: '{question}'\n\n"
        f"The following astrological placements were generated for this moment:\n{chart_text}"
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
        "HTTP-Referer": "https://github.com/reden/astrology", # Optional
        "X-Title": "OpenRouter Astrology", # Optional
    }

    console.print("\n[bold blue]Consulting the celestial spheres...[/bold blue]")

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
        description="Get an astrological reading using an LLM via OpenRouter.",
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

    console.print("[bold magenta]Welcome to Anthro Astrology[/bold magenta] ✨ (via OpenRouter)")
    console.print(f"[dim]Using model: {model_name}[/dim]")
    question = console.input("[bold yellow]Ask your cosmic question[/bold yellow]: ")

    console.print("\nChoose your reading type:")
    console.print("[green]1[/green]: Single Placement")
    console.print("[green]3[/green]: Three-Part Reading (Sun, Moon, Ascendant-like)")
    console.print("[green]10[/green]: Momentary Natal Chart")

    try:
        reading_choice = console.input("Your choice (1/3/10): ").strip()
        if not reading_choice:
            reading_type = 1
        else:
            reading_type = int(reading_choice)
    except ValueError:
        reading_type = 1

    if reading_type not in [1, 3, 10]:
        console.print("[red]Invalid choice. Defaulting to a single placement.[/red]")
        reading_type = 1

    generated_chart = generate_chart(question, reading_type)

    console.print(f"\n[bold cyan]Your Astrological Placements:[/bold cyan]")

    if reading_type == 10:
        positions = [
            "1. Self, Identity (Ascendant)", "2. Values, Possessions", "3. Communication, Siblings",
            "4. Home, Family, Roots (IC)", "5. Creativity, Romance, Children", "6. Health, Daily Routines",
            "7. Partnerships, Marriage (Descendant)", "8. Transformation, Shared Resources",
            "9. Philosophy, Travel, Higher Ed.", "10. Career, Public Life (Midheaven)"
        ]
        for i, placement in enumerate(generated_chart):
            console.print(f"[bold]{positions[i]}: {placement['planet']} in {placement['sign']} in the {placement['house']}[/bold]")
    else:
        for i, placement in enumerate(generated_chart):
            console.print(f"[bold]{i+1}. {placement['planet']} in {placement['sign']} in the {placement['house']}[/bold]")

    #interpretation = interpret_chart(question, generated_chart, model_name)
    #console.print(f"\n[italic green]{interpretation}[/italic green]\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]⏹️ Reading canceled.[/bold red]")
