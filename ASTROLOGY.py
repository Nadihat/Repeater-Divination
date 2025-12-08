import hashlib
import time
import os
import argparse
import math
from typing import List, Dict, Any
from rich import print
from rich.console import Console
from collections import defaultdict
from hashlib import pbkdf2_hmac

# === CONFIGURATION ===
THINK_DEPTH = 8888

console = Console()

# === ASTROLOGICAL DATA ===
MAJOR_PLANETS = [
    'Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto'
]
MINOR_BODIES = [
    'Ceres', 'Pallas', 'Juno', 'Vesta', 'Hygiea', 'Chiron', 'Pholus', 'Eris', 
    'Haumea', 'Makemake', 'Gonggong', 'Quaoar', 'Sedna', 'Orcus'
]

# === POWER SCORES ===
PLANET_POWER = {
    'Sun': 10, 'Moon': 9, 'Pluto': 8, 'Mars': 7, 'Jupiter': 7, 'Saturn': 7,
    'Mercury': 6, 'Uranus': 6, 'Neptune': 6, 'Venus': 5,
    'Ceres': 4, 'Chiron': 4, 'Pallas': 3, 'Juno': 3, 'Vesta': 3,
    'Hygiea': 2, 'Pholus': 2, 'Eris': 2, 'Haumea': 1, 'Makemake': 1,
    'Gonggong': 1, 'Quaoar': 1, 'Sedna': 1, 'Orcus': 1
}
SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]
HOUSES = [
    '1st House', '2nd House', '3rd House', '4th House', '5th House', '6th House',
    '7th House', '8th House', '9th House', '10th House', '11th House', '12th House'
]

ASPECTS = {
    # Major Aspects
    "Conjunction": {"type": "longitude", "angle": 0, "orb": 8.0, "power": 10},
    "Opposition": {"type": "longitude", "angle": 180, "orb": 8.0, "power": 9},
    "Square": {"type": "longitude", "angle": 90, "orb": 8.0, "power": 9},
    "Trine": {"type": "longitude", "angle": 120, "orb": 8.0, "power": 8},
    "Sextile": {"type": "longitude", "angle": 60, "orb": 6.0, "power": 6},
    
    # Minor Aspects
    "Quincunx": {"type": "longitude", "angle": 150, "orb": 2.0, "power": 5},
    "Semi-Square": {"type": "longitude", "angle": 45, "orb": 2.0, "power": 4},
    "Sesquisquare": {"type": "longitude", "angle": 135, "orb": 2.0, "power": 4},
    "Quintile": {"type": "longitude", "angle": 72, "orb": 2.0, "power": 4},
    "Biquintile": {"type": "longitude", "angle": 144, "orb": 2.0, "power": 4},
    "Septile": {"type": "longitude", "angle": 360/7, "orb": 1.5, "power": 3},
    "Bi-Septile": {"type": "longitude", "angle": 2 * (360/7), "orb": 1.5, "power": 3},
    "Tri-Septile": {"type": "longitude", "angle": 3 * (360/7), "orb": 1.5, "power": 3},
    "Semi-Sextile": {"type": "longitude", "angle": 30, "orb": 2.0, "power": 2},
    "Semi-Quintile": {"type": "longitude", "angle": 36, "orb": 1.5, "power": 2},
    "Quindecile": {"type": "longitude", "angle": 165, "orb": 2.0, "power": 2},
    "Novile": {"type": "longitude", "angle": 40, "orb": 1.5, "power": 1},
    "Bi-Novile": {"type": "longitude", "angle": 80, "orb": 1.5, "power": 1},
    "Quatro-Novile": {"type": "longitude", "angle": 160, "orb": 1.5, "power": 1},

    # Declination Aspects
    "Parallel": {"type": "declination", "orb": 1.0, "power": 7},
    "Contra-Parallel": {"type": "contra-declination", "orb": 1.0, "power": 6},
}

# === HASH FUNCTION ===
def hash_question(question: str, salt: str = "", times: int = THINK_DEPTH) -> int:
    # Add os.urandom for better entropy in the initial seed
    random_bytes = os.urandom(32)  # 32 bytes of cryptographically secure random data
    password = random_bytes + (question + salt).encode()
    # Use PBKDF2 with SHA-256 for cryptographically secure hashing
    h = pbkdf2_hmac('sha256', password, b'astrology_salt', times)
    return int.from_bytes(h, 'big')

# === CHART GENERATION ===
def generate_chart(question: str, count: int, include_minor_bodies: bool = False) -> List[Dict[str, Any]]:
    chart = []
    used_planets = set()
    used_houses = set()
    timestamp = int(time.time())
    
    available_planets = MAJOR_PLANETS + (MINOR_BODIES if include_minor_bodies else [])
    planets_to_use = available_planets[:count]

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

def calculate_orb_multiplier(orb_degrees: float) -> float:
    """Calculate orb multiplier based on exactness of aspect"""
    if orb_degrees <= 1.0:
        return 3.0
    elif orb_degrees <= 3.0:
        return 2.0
    elif orb_degrees <= 6.0:
        return 1.0
    else:
        return 0.5

def find_aspects_between_planets(p1: Dict, p2: Dict, is_transit: bool = False) -> List[Dict]:
    found = []
    p1_name = f"t.{p1['planet']}" if is_transit else p1['planet']
    p2_name = p2['planet']
    
    # Get planet power scores
    p1_power = PLANET_POWER.get(p1['planet'], 1)
    p2_power = PLANET_POWER.get(p2['planet'], 1)
    
    # Longitude aspects
    angle = abs(p1['total_degree'] - p2['total_degree'])
    if angle > 180:
        angle = 360 - angle
    
    for name, data in ASPECTS.items():
        if data['type'] == 'longitude':
            orb_diff = abs(angle - data['angle'])
            if orb_diff <= data['orb']:
                orb_multiplier = calculate_orb_multiplier(orb_diff)
                aspect_power = data['power']
                total_score = (p1_power + p2_power) * aspect_power * orb_multiplier
                
                found.append({
                    'description': f"{p1_name} {name} {p2_name}",
                    'score': total_score,
                    'orb': orb_diff,
                    'type': 'natal' if not is_transit else 'transit'
                })

    # Declination aspects
    declination1 = get_declination(p1['total_degree'])
    declination2 = get_declination(p2['total_degree'])
    
    # Parallel
    parallel_orb = abs(declination1 - declination2)
    if parallel_orb <= ASPECTS["Parallel"]["orb"]:
        orb_multiplier = calculate_orb_multiplier(parallel_orb)
        aspect_power = ASPECTS["Parallel"]["power"]
        total_score = (p1_power + p2_power) * aspect_power * orb_multiplier
        
        found.append({
            'description': f"{p1_name} Parallel {p2_name}",
            'score': total_score,
            'orb': parallel_orb,
            'type': 'natal' if not is_transit else 'transit'
        })
    
    # Contra-Parallel
    contra_parallel_orb = abs(declination1 + declination2)
    if contra_parallel_orb <= ASPECTS["Contra-Parallel"]["orb"]:
        orb_multiplier = calculate_orb_multiplier(contra_parallel_orb)
        aspect_power = ASPECTS["Contra-Parallel"]["power"]
        total_score = (p1_power + p2_power) * aspect_power * orb_multiplier
        
        found.append({
            'description': f"{p1_name} Contra-Parallel {p2_name}",
            'score': total_score,
            'orb': contra_parallel_orb,
            'type': 'natal' if not is_transit else 'transit'
        })
        
    return found

def calculate_aspects(natal_chart: List[Dict], transiting_chart: List[Dict] = None) -> Dict[str, List[Dict]]:
    all_aspects = []
    
    # Calculate natal aspects
    for i in range(len(natal_chart)):
        for j in range(i + 1, len(natal_chart)):
            p1 = natal_chart[i]
            p2 = natal_chart[j]
            found = find_aspects_between_planets(p1, p2)
            all_aspects.extend(found)
    
    # Calculate transit aspects
    if transiting_chart:
        for t_planet in transiting_chart:
            for n_planet in natal_chart:
                found = find_aspects_between_planets(t_planet, n_planet, is_transit=True)
                all_aspects.extend(found)
    
    # Sort by score (highest first) and take top 10
    all_aspects.sort(key=lambda x: x['score'], reverse=True)
    top_aspects = all_aspects[:10]
    
    # Separate into natal and transit for display
    natal_aspects = [asp for asp in top_aspects if asp['type'] == 'natal']
    transit_aspects = [asp for asp in top_aspects if asp['type'] == 'transit']
    
    return {"natal": natal_aspects, "transit": transit_aspects}


# === MAIN LOGIC ===
def main():
    parser = argparse.ArgumentParser(description="Get a comprehensive astrological reading.")
    parser.add_argument("-m", "--minor-bodies", action="store_true", help="Include minor bodies (asteroids, dwarf planets, centaurs) in the reading.")
    args = parser.parse_args()

    console.print("[bold magenta]Welcome to Anthro Astrology[/bold magenta] ✨")
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
        available_planets = MAJOR_PLANETS + (MINOR_BODIES if args.minor_bodies else [])
        num_bodies = len(available_planets)
        natal_chart = generate_chart(question, num_bodies, args.minor_bodies)
        transiting_chart = generate_chart(f"transits for {question}", num_bodies, args.minor_bodies)
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
            console.print(f"\n[bold cyan]Top Natal Aspects (by power):[/bold cyan]")
            for aspect in all_aspects["natal"]:
                console.print(f"- {aspect['description']} (Score: {aspect['score']:.1f}, Orb: {aspect['orb']:.1f}°)")
        
        if all_aspects["transit"]:
            console.print(f"\n[bold cyan]Top Transiting Aspects (by power):[/bold cyan]")
            for aspect in all_aspects["transit"]:
                console.print(f"- {aspect['description']} (Score: {aspect['score']:.1f}, Orb: {aspect['orb']:.1f}°)")

    else:
        count = 1 if reading_type == 1 else 3
        generated_chart = generate_chart(question, count, args.minor_bodies)
        console.print(f"\n[bold cyan]Your Astrological Placements:[/bold cyan]")
        for p in generated_chart:
            console.print(f"- {p['planet']} at {p['degree']}° {p['sign']} in the {p['house']}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]⏹️ Reading canceled.[/bold red]")
