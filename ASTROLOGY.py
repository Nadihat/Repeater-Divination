import hashlib
import requests
import time
import os
import argparse
import math
from typing import List, Dict, Any
from rich import print
from rich.console import Console
from collections import defaultdict

# === CONFIGURATION ===
DEFAULT_MODEL = "x-ai/grok-3-beta"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
THINK_DEPTH = 8888

console = Console()

# === ASTROLOGICAL DATA ===
PLANETS = [
    'Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto',
    'Ceres', 'Pallas', 'Juno', 'Vesta', 'Hygiea', 'Chiron', 'Pholus', 'Eris', 
    'Haumea', 'Makemake', 'Gonggong', 'Quaoar', 'Sedna', 'Orcus'
]
SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]
HOUSES = [
    '1st House', '2nd House', '3rd House', '4th House', '5th House', '6th House',
    '7th House', '8th House', '9th House', '10th House', '11th House', '12th House'
]

ASPECTS = {
    # Major Aspects
    "Conjunction": {"type": "longitude", "angle": 0, "orb": 8.0},
    "Sextile": {"type": "longitude", "angle": 60, "orb": 6.0},
    "Square": {"type": "longitude", "angle": 90, "orb": 8.0},
    "Trine": {"type": "longitude", "angle": 120, "orb": 8.0},
    "Opposition": {"type": "longitude", "angle": 180, "orb": 8.0},
    
    # Minor Aspects
    "Quincunx": {"type": "longitude", "angle": 150, "orb": 2.0},
    "Semi-Sextile": {"type": "longitude", "angle": 30, "orb": 2.0},
    "Semi-Square": {"type": "longitude", "angle": 45, "orb": 2.0},
    "Sesquisquare": {"type": "longitude", "angle": 135, "orb": 2.0},
    
    # Quintile Series
    "Quintile": {"type": "longitude", "angle": 72, "orb": 2.0},
    "Biquintile": {"type": "longitude", "angle": 144, "orb": 2.0},
    "Semi-Quintile": {"type": "longitude", "angle": 36, "orb": 1.5},

    # Septile Series
    "Septile": {"type": "longitude", "angle": 360/7, "orb": 1.5},
    "Bi-Septile": {"type": "longitude", "angle": 2 * (360/7), "orb": 1.5},
    "Tri-Septile": {"type": "longitude", "angle": 3 * (360/7), "orb": 1.5},

    # Novile Series
    "Novile": {"type": "longitude", "angle": 40, "orb": 1.5},
    "Bi-Novile": {"type": "longitude", "angle": 80, "orb": 1.5},
    "Quatro-Novile": {"type": "longitude", "angle": 160, "orb": 1.5},

    # Other
    "Quindecile": {"type": "longitude", "angle": 165, "orb": 2.0},

    # Declination Aspects
    "Parallel": {"type": "declination", "orb": 1.0},
    "Contra-Parallel": {"type": "contra-declination", "orb": 1.0},
}

# === HASH FUNCTION ===
def hash_question(question: str, salt: str = "", times: int = THINK_DEPTH) -> int:
    # Add os.urandom for better entropy in the initial seed
    random_bytes = os.urandom(32)  # 32 bytes of cryptographically secure random data
    h = random_bytes + (question + salt).encode()
    for _ in range(times):
        h = hashlib.sha512(h).digest()
    return int.from_bytes(h, 'big')

# === CHART GENERATION ===
def generate_chart(question: str, count: int) -> List[Dict[str, Any]]:
    chart = []
    used_planets = set()
    used_houses = set()
    timestamp = int(time.time())
    planets_to_use = PLANETS[:count]

    for i in range(len(planets_to_use)):
        planet = planets_to_use[i]
        salt = f"{question}-placement-{planet}-{timestamp}"
        
        total_degree = hash_question(question, salt + "degree") % 360
        sign_index = total_degree // 30
        degree_in_sign = total_degree % 30
        sign = SIGNS[sign_index]

        # Allow houses to be duplicated since there are more bodies than houses
        house_index = hash_question(question, salt + "house") % len(HOUSES)
        house = HOUSES[house_index]

        chart.append({
            "planet": planet, 
            "sign": sign, 
            "degree": degree_in_sign,
            "total_degree": total_degree,
            "house": house
        })
    return chart

# === PARALLEL & ASPECT CALCULATION ===
def find_parallels(chart: List[Dict[str, Any]]) -> Dict[str, Dict[str, List[str]]]:
    signs_map = defaultdict(list)
    for p in chart:
        signs_map[p['sign']].append(p['planet'])
    houses_map = defaultdict(list)
    for p in chart:
        houses_map[p['house']].append(p['planet'])
    sign_parallels = {sign: planets for sign, planets in signs_map.items() if len(planets) > 1}
    house_parallels = {house: planets for house, planets in houses_map.items() if len(planets) > 1}
    return {"by_sign": sign_parallels, "by_house": house_parallels}

def get_declination(total_degree: int) -> float:
    return 23.45 * math.sin(math.radians(total_degree))

def find_aspects_between_planets(p1: Dict, p2: Dict, is_transit: bool = False) -> List[str]:
    found = []
    p1_name = f"t.{p1['planet']}" if is_transit else p1['planet']
    p2_name = p2['planet']
    
    # Longitude aspects
    angle = abs(p1['total_degree'] - p2['total_degree'])
    if angle > 180:
        angle = 360 - angle
    for name, data in ASPECTS.items():
        if data['type'] == 'longitude':
            if abs(angle - data['angle']) <= data['orb']:
                found.append(f"{p1_name} {name} {p2_name}")

    # Declination aspects
    declination1 = get_declination(p1['total_degree'])
    declination2 = get_declination(p2['total_degree'])
    if abs(declination1 - declination2) <= ASPECTS["Parallel"]["orb"]:
        found.append(f"{p1_name} Parallel {p2_name}")
    if abs(declination1 + declination2) <= ASPECTS["Contra-Parallel"]["orb"]:
        found.append(f"{p1_name} Contra-Parallel {p2_name}")
        
    return found

def calculate_aspects(natal_chart: List[Dict], transiting_chart: List[Dict] = None) -> Dict[str, List[str]]:
    aspects = {"natal": [], "transit": []}
    for i in range(len(natal_chart)):
        for j in range(i + 1, len(natal_chart)):
            p1 = natal_chart[i]
            p2 = natal_chart[j]
            found = find_aspects_between_planets(p1, p2)
            if found:
                aspects["natal"].extend(found)
    if transiting_chart:
        for t_planet in transiting_chart:
            for n_planet in natal_chart:
                found = find_aspects_between_planets(t_planet, n_planet, is_transit=True)
                if found:
                    aspects["transit"].extend(found)
    return aspects

# === INTERPRETATION REQUEST ===
def interpret_chart(
    question: str, 
    chart: List[Dict[str, Any]], 
    model: str, 
    transiting_chart: List[Dict[str, Any]] = None, 
    parallels: Dict = None,
    natal_aspects: List[str] = None,
    transit_aspects: List[str] = None
) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "[red]❌ OPENROUTER_API_KEY not set.[/red]"

    chart_text = "\n".join([f"- {p['planet']} at {p['degree']}° {p['sign']} in the {p['house']}" for p in chart])

    system_prompt = (
        "You are a wise and mystical astrologer. Provide a deep, insightful, and spiritual reading. "
        "The reading includes traditional planets, asteroids (Ceres, Pallas, Juno, Vesta), and dwarf planets/centaurs. "
        "Interpret these additional bodies as nuanced layers of the psyche and spiritual journey. "
        "Combine all provided data (natal placements, transits, parallels, aspects) into a holistic narrative."
    )
    user_prompt = f"The question is: '{question}'\n\nNatal Chart:\n{chart_text}"

    if parallels and (parallels["by_sign"] or parallels["by_house"]):
        parallels_text = ""
        if parallels["by_sign"]:
            parallels_text += "\n\nStelliums (Parallels by Sign):\n"
            for sign, planets in parallels["by_sign"].items():
                parallels_text += f"- In {sign}: {', '.join(planets)}\n"
        if parallels["by_house"]:
            parallels_text += "\nStelliums (Parallels by House):\n"
            for house, planets in parallels["by_house"].items():
                parallels_text += f"- In {house}: {', '.join(planets)}\n"
        user_prompt += parallels_text
        system_prompt += "\nInterpret the stelliums as areas of concentrated energy."

    if transiting_chart:
        transiting_lines = [f"- {p['planet']} at {p['degree']}° {p['sign']}" for p in transiting_chart]
        user_prompt += "\n\nTransiting Planets (Current Sky):\n" + "\n".join(transiting_lines)
        system_prompt += "\nAnalyze the transiting planets in relation to the natal chart."

    if natal_aspects:
        user_prompt += "\n\nNatal Aspects (Core Dynamics):\n" + ", ".join(natal_aspects)
        system_prompt += "\nInterpret the natal aspects. These reveal deep-seated psychological patterns and spiritual gifts."

    if transit_aspects:
        user_prompt += "\n\nTransiting Aspects (Current Influences):\n" + ", ".join(transit_aspects)
        system_prompt += "\nInterpret the transiting aspects. These highlight current themes and opportunities."

    payload = {"model": model, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=300)
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response.")
    except Exception as e:
        return f"[red]An error occurred: {e}[/red]"

# === MAIN LOGIC ===
def main():
    parser = argparse.ArgumentParser(description="Get a comprehensive astrological reading.")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Model to use from OpenRouter.")
    args = parser.parse_args()

    console.print("[bold magenta]Welcome to Anthro Astrology[/bold magenta] ✨ (Super Reading Edition)")
    question = console.input("[bold yellow]Ask your cosmic question[/bold yellow]: ")

    console.print("\nChoose your reading type:")
    console.print("[green]1[/green]: Single Placement")
    console.print("[green]3[/green]: Three-Part Reading")
    console.print("[bold green]13[/bold green]: Super Comprehensive Reading")

    try:
        reading_type = int(console.input("Your choice (1/3/13): ").strip() or 13)
    except ValueError:
        reading_type = 13

    if reading_type == 13:
        console.print("\n[bold blue]Generating a Super Comprehensive Reading...[/bold blue]")
        num_bodies = len(PLANETS)
        natal_chart = generate_chart(question, num_bodies)
        transiting_chart = generate_chart(f"transits for {question}", num_bodies)
        parallels = find_parallels(natal_chart)
        all_aspects = calculate_aspects(natal_chart, transiting_chart)

        console.print(f"\n[bold cyan]Your Natal Chart:[/bold cyan]")
        for p in natal_chart:
            console.print(f"- {p['planet']} at {p['degree']}° {p['sign']} in the {p['house']}")

        console.print(f"\n[bold cyan]Transiting Planets:[/bold cyan]")
        for p in transiting_chart:
            console.print(f"- {p['planet']} at {p['degree']}° {p['sign']}")

        if parallels["by_sign"] or parallels["by_house"]:
            console.print(f"\n[bold cyan]Stelliums/Parallels:[/bold cyan]")
            for sign, planets in parallels["by_sign"].items(): console.print(f"- In {sign}: {', '.join(planets)}")
            for house, planets in parallels["by_house"].items(): console.print(f"- In {house}: {', '.join(planets)}")
        
        if all_aspects["natal"]:
            console.print(f"\n[bold cyan]Natal Aspects:[/bold cyan]")
            console.print(", ".join(all_aspects["natal"]))
        
        if all_aspects["transit"]:
            console.print(f"\n[bold cyan]Transiting Aspects:[/bold cyan]")
            console.print(", ".join(all_aspects["transit"]))

        console.print("\n[bold blue]Consulting the celestial spheres for your interpretation...[/bold blue]")
        interpretation = interpret_chart(
            question, natal_chart, args.model,
            transiting_chart=transiting_chart,
            parallels=parallels,
            natal_aspects=all_aspects["natal"],
            transit_aspects=all_aspects["transit"]
        )
        console.print(f"\n[italic green]{interpretation}[/italic green]\n")

    else:
        count = 1 if reading_type == 1 else 3
        generated_chart = generate_chart(question, count)
        console.print(f"\n[bold cyan]Your Astrological Placements:[/bold cyan]")
        for p in generated_chart:
            console.print(f"- {p['planet']} at {p['degree']}° {p['sign']} in the {p['house']}")
        interpretation = interpret_chart(question, generated_chart, args.model)
        console.print(f"\n[italic green]{interpretation}[/italic green]\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]⏹️ Reading canceled.[/bold red]")
