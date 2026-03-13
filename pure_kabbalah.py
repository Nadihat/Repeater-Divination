#!/usr/bin/env python3
"""
KABBALAH9.py
Kabbalistic readings based on true randomness.

This version provides non-deterministic, non-interactive readings based on a user's query.
It fetches a large pool of true atmospheric entropy from Random.org to select the pathways
and specifically determine the states (Excessive, Deficient, Balanced).

Usage:
    python3 KABBALAH9.py -q "Your question here" [options]

Options:
    -r, --reading-type [1|3|10|4]  Selects the type of reading. (Default: 3)
    -p, --paths N                  Specify the number of paths to draw. (Default: drawn randomly)
"""

import sys
import argparse
import urllib.request
import random
import hashlib
from typing import List, Tuple
from rich import print
from rich.console import Console

# === CONFIGURATION ===
NUM_PATHS = 22 # The 22 Paths of the Tree of Life
console = Console()

# === KABBALISTIC DATA ===
sephirot_names = [
    'Keter (Crown)', 'Chokmah (Wisdom)', 'Binah (Understanding)', 'Chesed (Mercy)',
    'Gevurah (Strength)', 'Tiferet (Beauty)', 'Netzach (Victory)', 'Hod (Splendor)',
    'Yesod (Foundation)', 'Malkuth (Kingdom)'
]

paths = [
    "Path of Aleph (Air)", "Path of Beth (Mercury)", "Path of Gimel (Moon)",
    "Path of Daleth (Venus)", "Path of Heh (Aries)", "Path of Vav (Taurus)",
    "Path of Zayin (Gemini)", "Path of Cheth (Cancer)", "Path of Teth (Leo)",
    "Path of Yod (Virgo)", "Path of Kaph (Jupiter)", "Path of Lamed (Libra)",
    "Path of Mem (Water)", "Path of Nun (Scorpio)", "Path of Samekh (Sagittarius)",
    "Path of Ayin (Capricorn)", "Path of Peh (Mars)", "Path of Tzaddi (Aquarius)",
    "Path of Qoph (Pisces)", "Path of Resh (Sun)", "Path of Shin (Fire)",
    "Path of Tav (Saturn)"
]

worlds = {
    "Archetypal": ['Keter (Crown)', 'Chokmah (Wisdom)', 'Binah (Understanding)'],
    "Creative": ['Chesed (Mercy)', 'Gevurah (Strength)', 'Tiferet (Beauty)'],
    "Formative": ['Netzach (Victory)', 'Hod (Splendor)', 'Yesod (Foundation)'],
    "Material": ['Malkuth (Kingdom)']
}

# The Five Worlds - Atmospheric Filters
FIVE_WORLDS = {
    "Atziluth": {
        "name": "Atziluth (Fire/Emanation)",
        "description": "High Potential, Low Resistance - Energy flows like light"
    },
    "Briah": {
        "name": "Briah (Air/Creation)",
        "description": "High Intelligence, Fast Movement - Energy flows like sound"
    },
    "Yetzirah": {
        "name": "Yetzirah (Water/Formation)",
        "description": "High Sensitivity, Swirling Flow - Energy flows like a river"
    },
    "Assiah": {
        "name": "Assiah (Earth/Action)",
        "description": "High Density, High Resistance - Energy flows like lava"
    },
    "Ain Sof Aur": {
        "name": "Ain Sof Aur (Limitless Light)",
        "description": "No World - Default reading with no atmospheric modifications"
    }
}

# === RANDOM READING LOGIC ===

def safe_pop(pool: List[int]) -> int:
    """Pops a true random number from the pool, or falls back to PRNG if empty."""
    return pool.pop() if pool else random.randint(0, 255)

def determine_state(true_random_val: int) -> str:
    """Maps a 0-255 random value to a Balanced, Excessive, or Deficient state."""
    # Convert 0-255 to a 1-100 scale
    val = (true_random_val % 100) + 1
    
    # 60% Balanced, 20% Excessive, 20% Deficient
    if val <= 60:
        return "Balanced"
    elif val <= 80:
        return "Excessive"
    else:
        return "Deficient"

def get_sephirot_reading(count: int, entropy_pool: List[int]) -> List[Tuple[str, str]]:
    """Randomly select Sephirot and assign states using true random numbers."""
    result = []
    
    # Da'at (The Abyss) has a 15% chance of appearing in any reading
    daat_check = (safe_pop(entropy_pool) % 100) + 1
    if daat_check <= 15:
        # Determine Da'at state (50/50 Excessive or Deficient)
        daat_state_val = safe_pop(entropy_pool)
        daat_state = "Excessive" if daat_state_val % 2 == 0 else "Deficient"
        
        result.append(('Da\'at (Knowledge)', daat_state))
        if daat_state == "Excessive":
            console.print("[bold yellow]⚡ REVELATION: The Abyss (Da'at) is Bridged! ⚡[/bold yellow]")
        elif daat_state == "Deficient":
            console.print("[dim]The Abyss is Silent (Deficient Da'at)[/dim]")

    # Select the requested Sephirot
    safe_count = min(count, len(sephirot_names))
    if safe_count == 10:
        chosen_names = sephirot_names.copy()
    else:
        chosen_names = random.sample(sephirot_names, safe_count)

    # Assign Exc/Def/Bal using the true random pool
    for name in chosen_names:
        state = determine_state(safe_pop(entropy_pool))
        result.append((name, state))

    return result

def get_paths_reading(count: int, entropy_pool: List[int]) -> List[Tuple[str, str]]:
    """Randomly selects Paths and assigns states using true random numbers."""
    if count == 0:
        return []

    safe_count = min(count, len(paths))
    chosen_paths = random.sample(paths, safe_count)
    
    result = []
    for path_name in chosen_paths:
        state = determine_state(safe_pop(entropy_pool))
        result.append((path_name, state))

    return result

def get_random_org_data(num_integers: int = 256) -> List[int]:
    """Fetches a large pool of true atmospheric randomness from the Random.org API."""
    url = f"https://www.random.org/integers/?num={num_integers}&min=0&max=255&col=1&base=10&format=plain&rnd=new"

    headers = {
        'User-Agent': 'Kabbalah-Divination/9.0'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        response = urllib.request.urlopen(req)
        data = response.read().decode('utf-8').strip()

        if data.startswith("Error:"):
            print(f"Random.org refused the request. {data}", file=sys.stderr)
            sys.exit(1)

        byte_list = [int(x) for x in data.split('\n') if x.strip()]
        return byte_list

    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: Random.org is unavailable or quota exceeded.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Network error: {e}", file=sys.stderr)
        sys.exit(1)

# === MAIN LOGIC ===
def main():
    parser = argparse.ArgumentParser(
        description="Kabbalistic readings based on true atmospheric randomness.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-q', '--query', required=True, help='Your sacred query.')
    parser.add_argument(
        '-r', '--reading-type',
        choices=['0', '1', '3', '10', '4'],
        default='3',
        help="""Type of reading:
0: Automatic (1-10 based on query)
1: Single Sephirah & Path
3: Mind/Heart/Body Pillar Reading (default)
10: Full Tree of Life
4: Four Worlds Reading"""
    )
    parser.add_argument(
        '-p', '--paths',
        type=int,
        help=f"Number of paths to draw (0-{NUM_PATHS}). If not specified, a number is drawn randomly."
    )
    args = parser.parse_args()

    question = args.query
    revelation_choice = args.reading_type

    # 1. Fetch a large pool of True Entropy (256 integers)
    entropy_data = get_random_org_data(256)
    
    # 2. Split the entropy. 
    # Use the first 32 bytes to securely seed Python's random choice engine (for node selections).
    # Use the rest as a raw pool to directly calculate Exc/Def/Bal states.
    seed_bytes = bytes(entropy_data[:32])
    entropy_pool = entropy_data[32:]

    random.seed(seed_bytes + question.encode('utf-8'))

    # Generate Auth Hash String for display
    auth_string = hashlib.sha256(seed_bytes).hexdigest()[:8].upper()

    # Select the World
    selected_world_key = random.choice(list(FIVE_WORLDS.keys()))
    selected_world = FIVE_WORLDS[selected_world_key]

    console.print(f"[bold purple]Kabbalistic Divination for:[/bold purple] '{question}'")
    console.print(f"[dim]Entropy Source:[/dim] Random.org (True Atmospheric Noise)", highlight=False)
    console.print(f"[dim]Auth:[/dim] [bold green]{auth_string}[/bold green]")
    console.print(f"[bold cyan]World:[/bold cyan] {selected_world['name']}")
    console.print(f"[dim]{selected_world['description']}[/dim]\n")

    # Determine sephirot count
    if revelation_choice == '4':
        sephirot_count = 10
        revealed_sephirot_with_states = get_sephirot_reading(10, entropy_pool)
    elif revelation_choice == '0':
        sephirot_count = random.randint(1, 10)
        revealed_sephirot_with_states = get_sephirot_reading(sephirot_count, entropy_pool)
    elif revelation_choice == '10':
        sephirot_count = 10
        revealed_sephirot_with_states = get_sephirot_reading(10, entropy_pool)
    else: 
        sephirot_count = int(revelation_choice)
        revealed_sephirot_with_states = get_sephirot_reading(sephirot_count, entropy_pool)

    # Determine path count
    if args.paths is not None:
        path_count = args.paths
        if not (0 <= path_count <= NUM_PATHS):
            console.print(f"[red]Error: Path count must be between 0 and {NUM_PATHS}.[/red]")
            return
    else:
        path_count = random.randint(0, NUM_PATHS)

    revealed_paths_with_states = get_paths_reading(path_count, entropy_pool)

    # --- Display Results ---
    console.print("[bold magenta]The Revealed Sephiroth:[/bold magenta]")
    
    def format_state(st):
        if st == "Balanced":
            return f"([green]{st}[/green])"
        elif st == "Excessive":
            return f"([bold red]{st}[/bold red])"
        else:
            return f"([blue]{st}[/blue])"
            
    if revelation_choice == '4':
        world_readings = {world_name: [] for world_name in worlds}
        for sephirah, state in revealed_sephirot_with_states:
            for world_name, sephirot_in_world in worlds.items():
                if sephirah in sephirot_in_world:
                    world_readings[world_name].append(f"{sephirah} {format_state(state)}")
                    
        for world_name, readings in world_readings.items():
            if readings:
                console.print(f"[bold]{world_name} World:[/bold] {', '.join(readings)}")
    else:
        for i, (s_name, state) in enumerate(revealed_sephirot_with_states):
            console.print(f"[bold]{i+1}. {s_name}[/bold] {format_state(state)}")

    if revealed_paths_with_states:
        console.print(f"\n[bold magenta]The Revealed Paths:[/bold magenta]")
        for i, (p_name, state) in enumerate(revealed_paths_with_states):
            console.print(f"[bold]{i+1}. {p_name}[/bold] {format_state(state)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("[bold red]⏹️ Revelation canceled.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
