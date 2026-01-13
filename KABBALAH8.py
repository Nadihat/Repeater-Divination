#!/usr/bin/env python3
"""
KABBALAH8.py
Kabbalistic readings based on cryptographic hashing and true randomness from os.urandom.

This version provides non-deterministic, non-interactive, and truly random readings based on a user's query,
inspired by the automatic nature of I-CHING3.py. It uses os.urandom for its primary source of entropy,
and a strong key derivation function (PBKDF2) to derive further values.

Usage:
    python3 KABBALAH6.py -q "Your question here" [options]

Options:
    -r, --reading-type [1|3|10|4]  Selects the type of reading. (Default: 3)
    -p, --paths N                  Specify the number of paths to draw. (Default: derived from query)
"""

import hashlib
import sys
import argparse
import math
from os import urandom
from typing import List, Tuple, Dict
from rich import print
from rich.console import Console
from datetime import datetime, timezone

# === CONFIGURATION ===
NUM_PATHS = 22 # The 22 Paths of the Tree of Life
console = Console()

# === KABBALISTIC DATA ===
sephirot_names = [
    'Keter (Crown)', 'Chokmah (Wisdom)', 'Binah (Understanding)', 'Chesed (Mercy)',
    'Gevurah (Strength)', 'Tiferet (Beauty)', 'Netzach (Victory)', 'Hod (Splendor)',
    'Yesod (Foundation)', 'Malkuth (Kingdom)'
]

# Tree of Life connection map - each Sephirah and its connected neighbors
TREE_MAP = {
    'Keter (Crown)': ['Chokmah (Wisdom)', 'Binah (Understanding)', 'Tiferet (Beauty)'],
    'Chokmah (Wisdom)': ['Keter (Crown)', 'Binah (Understanding)', 'Chesed (Mercy)', 'Tiferet (Beauty)'],
    'Binah (Understanding)': ['Keter (Crown)', 'Chokmah (Wisdom)', 'Gevurah (Strength)', 'Tiferet (Beauty)'],
    'Chesed (Mercy)': ['Chokmah (Wisdom)', 'Gevurah (Strength)', 'Tiferet (Beauty)', 'Netzach (Victory)'],
    'Gevurah (Strength)': ['Binah (Understanding)', 'Chesed (Mercy)', 'Tiferet (Beauty)', 'Hod (Splendor)'],
    'Tiferet (Beauty)': ['Keter (Crown)', 'Chokmah (Wisdom)', 'Binah (Understanding)', 'Chesed (Mercy)', 'Gevurah (Strength)', 'Netzach (Victory)', 'Hod (Splendor)', 'Yesod (Foundation)'],
    'Netzach (Victory)': ['Chesed (Mercy)', 'Tiferet (Beauty)', 'Hod (Splendor)', 'Yesod (Foundation)', 'Malkuth (Kingdom)'],
    'Hod (Splendor)': ['Gevurah (Strength)', 'Tiferet (Beauty)', 'Netzach (Victory)', 'Yesod (Foundation)', 'Malkuth (Kingdom)'],
    'Yesod (Foundation)': ['Tiferet (Beauty)', 'Netzach (Victory)', 'Hod (Splendor)', 'Malkuth (Kingdom)'],
    'Malkuth (Kingdom)': ['Netzach (Victory)', 'Hod (Splendor)', 'Yesod (Foundation)']
}

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

# Mapping of the 22 Paths to their connecting Sephirot (based on traditional Tree of Life)
PATH_CONNECTIONS = {
    "Path of Aleph (Air)": ("Keter (Crown)", "Chokmah (Wisdom)"),
    "Path of Beth (Mercury)": ("Keter (Crown)", "Binah (Understanding)"),
    "Path of Gimel (Moon)": ("Keter (Crown)", "Tiferet (Beauty)"),
    "Path of Daleth (Venus)": ("Chokmah (Wisdom)", "Binah (Understanding)"),
    "Path of Heh (Aries)": ("Chokmah (Wisdom)", "Tiferet (Beauty)"),
    "Path of Vav (Taurus)": ("Chokmah (Wisdom)", "Chesed (Mercy)"),
    "Path of Zayin (Gemini)": ("Binah (Understanding)", "Tiferet (Beauty)"),
    "Path of Cheth (Cancer)": ("Binah (Understanding)", "Gevurah (Strength)"),
    "Path of Teth (Leo)": ("Chesed (Mercy)", "Gevurah (Strength)"),
    "Path of Yod (Virgo)": ("Chesed (Mercy)", "Tiferet (Beauty)"),
    "Path of Kaph (Jupiter)": ("Chesed (Mercy)", "Netzach (Victory)"),
    "Path of Lamed (Libra)": ("Gevurah (Strength)", "Tiferet (Beauty)"),
    "Path of Mem (Water)": ("Gevurah (Strength)", "Hod (Splendor)"),
    "Path of Nun (Scorpio)": ("Tiferet (Beauty)", "Netzach (Victory)"),
    "Path of Samekh (Sagittarius)": ("Tiferet (Beauty)", "Yesod (Foundation)"),
    "Path of Ayin (Capricorn)": ("Tiferet (Beauty)", "Hod (Splendor)"),
    "Path of Peh (Mars)": ("Netzach (Victory)", "Hod (Splendor)"),
    "Path of Tzaddi (Aquarius)": ("Netzach (Victory)", "Yesod (Foundation)"),
    "Path of Qoph (Pisces)": ("Netzach (Victory)", "Malkuth (Kingdom)"),
    "Path of Resh (Sun)": ("Hod (Splendor)", "Yesod (Foundation)"),
    "Path of Shin (Fire)": ("Hod (Splendor)", "Malkuth (Kingdom)"),
    "Path of Tav (Saturn)": ("Yesod (Foundation)", "Malkuth (Kingdom)")
}

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
        "description": "High Potential, Low Resistance - Energy flows like light",
        "decay_divisor": 8000.0
    },
    "Briah": {
        "name": "Briah (Air/Creation)", 
        "description": "High Intelligence, Fast Movement - Energy flows like sound",
        "decay_divisor": 6000.0
    },
    "Yetzirah": {
        "name": "Yetzirah (Water/Formation)",
        "description": "High Sensitivity, Swirling Flow - Energy flows like a river", 
        "decay_divisor": 4000.0
    },
    "Assiah": {
        "name": "Assiah (Earth/Action)",
        "description": "High Density, High Resistance - Energy flows like lava",
        "decay_divisor": 2000.0
    },
    "Ain Sof Aur": {
        "name": "Ain Sof Aur (Limitless Light)",
        "description": "No World - Default reading with no atmospheric modifications",
        "decay_divisor": 5000.0
    }
}

# === HASHING ENGINE ===
class ProtectiveHasher:
    PROTECTION_ITERATIONS = 88_888
    HASH_LENGTH = 32

    @staticmethod
    def derive_protected_bytes(base_bytes: bytes, salt_bytes: bytes) -> bytes:
        try:
            return hashlib.pbkdf2_hmac(
                'sha256', base_bytes, salt_bytes,
                ProtectiveHasher.PROTECTION_ITERATIONS,
                dklen=ProtectiveHasher.HASH_LENGTH
            )
        except Exception as e:
            print(f"Warning: Using fallback hashing method: {e}", file=sys.stderr)
            result = base_bytes
            for _ in range(ProtectiveHasher.PROTECTION_ITERATIONS):
                result = hashlib.sha256(result + salt_bytes).digest()
            return result[:ProtectiveHasher.HASH_LENGTH]

def hash_for_int(seed: bytes, question: str, salt: str = "") -> int:
    # Combine random bytes + question + salt for cryptographic hashing
    password = seed + (question + salt).encode("utf-8")
    salt_bytes = b'kabbalah_salt'
    hashed_bytes = ProtectiveHasher.derive_protected_bytes(password, salt_bytes)
    return int.from_bytes(hashed_bytes, 'big')

# === FLOW-BASED READING LOGIC ===
def select_world(seed: bytes, question: str) -> dict:
    """Select one of the Five Worlds based on the question hash."""
    world_keys = list(FIVE_WORLDS.keys())
    salt = "world-selection"
    world_index = hash_for_int(seed, question, salt) % len(world_keys)
    selected_key = world_keys[world_index]
    return FIVE_WORLDS[selected_key]

def calculate_path_conductivity(seed: bytes, question: str, sephirah1: str, sephirah2: str, decay_divisor: float = 5000.0) -> float:
    """Calculate how 'open' or 'closed' a path is between two Sephirot."""
    # Create a consistent path key regardless of direction
    path_key = tuple(sorted([sephirah1, sephirah2]))
    salt = f"path-conductivity-{path_key[0]}-{path_key[1]}"
    raw_val = hash_for_int(seed, question, salt) % 10000
    # Use exponential decay to create conductivity score (0.0 to 1.0)
    # The decay_divisor is modified by the selected World
    return math.exp(-raw_val / decay_divisor)

def get_sephirot_reading(seed: bytes, question: str, count: int, selected_world: dict) -> List[Tuple[str, str]]:
    """
    Calculate Sephirot states based on energy flow through the Tree of Life network.
    """
    # --- PHASE 1: GLOBAL SIMULATION ---
    # We must simulate the entire tree to establish the "Ambient Pressure" (Mean/StdDev).
    # Without this, single-sephirah readings have a StdDev of 0, causing Da'at to trigger constantly.

    # 1.1 Generate Base Potentials for ALL 10
    potentials = {}
    for name in sephirot_names:
        salt_a = f"potential-{name}-a"
        salt_b = f"potential-{name}-b"
        roll_a = hash_for_int(seed, question, salt_a) % 100
        roll_b = hash_for_int(seed, question, salt_b) % 100
        potentials[name] = (roll_a + roll_b) / 2

    # 1.2 Calculate Connectivity for ALL Paths
    decay_divisor = selected_world["decay_divisor"]
    path_conductivities = {}
    for sephirah, neighbors in TREE_MAP.items():
        for neighbor in neighbors:
            conductivity = calculate_path_conductivity(seed, question, sephirah, neighbor, decay_divisor)
            path_conductivities[(sephirah, neighbor)] = conductivity

    # 1.3 Calculate Pressure (Net Flow) for ALL 10
    all_pressures = {}
    pressure_values = []

    for name in sephirot_names:
        neighbors = TREE_MAP[name]
        inflow = 0.0
        outflow = 0.0

        for neighbor in neighbors:
            # Inflow (Neighbor -> Me)
            c_in = path_conductivities.get((neighbor, name), 0.0)
            inflow += potentials[neighbor] * c_in
            # Outflow (Me -> Neighbor)
            c_out = path_conductivities.get((name, neighbor), 0.0)
            outflow += potentials[name] * c_out

        net_pressure = inflow - outflow
        all_pressures[name] = net_pressure
        pressure_values.append(net_pressure)

    # 1.4 Calculate Global Statistics
    abs_pressures = [abs(p) for p in pressure_values]
    mean_pressure = sum(abs_pressures) / len(abs_pressures)
    variance = sum((p - mean_pressure) ** 2 for p in abs_pressures) / len(abs_pressures)
    std_dev = math.sqrt(variance) if variance > 0 else 1.0

    threshold = std_dev * 0.8

    # --- PHASE 2: DA'AT CALCULATION ---
    # Da'at is an emergent property of the gap between Head and Heart.
    supernal_inflow = (potentials['Keter (Crown)'] + potentials['Chokmah (Wisdom)'] + potentials['Binah (Understanding)']) / 3
    tiferet_outflow = potentials['Tiferet (Beauty)']
    daat_tension = abs(supernal_inflow - tiferet_outflow)

    sigma_multiplier = 1.8 # Da'at only appears if tension is 1.8x the standard deviation
    daat_state = None

    if daat_tension > (mean_pressure + (std_dev * sigma_multiplier)):
        daat_state = "Excessive"
    elif daat_tension < (mean_pressure - (std_dev * sigma_multiplier)):
        daat_state = "Deficient"

    # --- PHASE 3: SELECTION & RESULT ---
    result = []

    # Insert Da'at if active
    if daat_state:
        result.append(('Da\'at (Knowledge)', daat_state))
        if daat_state == "Excessive":
            console.print("[bold yellow]⚡ REVELATION: The Abyss (Da'at) is Bridged! ⚡[/bold yellow]")
        elif daat_state == "Deficient":
            console.print("[dim]The Abyss is Silent (Deficient Da'at)[/dim]")

    # Select the requested Sephirot
    if count >= 10:
        chosen_names = sephirot_names
    else:
        available_sephirot = sephirot_names.copy()
        chosen_names = []
        for i in range(count):
            salt = f"sephirah-name-{i}"
            index = hash_for_int(seed, question, salt) % len(available_sephirot)
            chosen_names.append(available_sephirot.pop(index))

    # Assign states based on the GLOBAL threshold
    for name in chosen_names:
        pressure = all_pressures[name]
        if pressure > threshold:
            state = 'Excessive'
        elif pressure < -threshold:
            state = 'Deficient'
        else:
            state = 'Normal'
        result.append((name, state))

    return result

def get_paths_reading(seed: bytes, question: str, count: int, selected_world: dict) -> List[Tuple[str, str]]:
    """Deterministically selects Paths and calculates their flow states based on the question."""
    if count == 0:
        return []
    
    # Step 1: Select paths
    available_paths = paths.copy()
    chosen_paths = []
    for i in range(count):
        salt = f"path-{i}"
        index = hash_for_int(seed, question, salt) % len(available_paths)
        chosen_paths.append(available_paths.pop(index))
    
    # Step 2: Calculate Sephirot potentials (needed for path flow calculations)
    potentials = {}
    for name in sephirot_names:
        salt = f"potential-{name}"
        potentials[name] = hash_for_int(seed, question, salt) % 100
    
    # Step 3: Calculate path flow states
    path_flows = []
    result = []
    
    for path_name in chosen_paths:
        if path_name not in PATH_CONNECTIONS:
            # Fallback for any missing connections
            result.append((path_name, 'Normal'))
            path_flows.append(0.0)
            continue
            
        seph1, seph2 = PATH_CONNECTIONS[path_name]
        
        # Calculate conductivity for this specific path (modified by World)
        decay_divisor = selected_world["decay_divisor"]
        conductivity = calculate_path_conductivity(seed, question, seph1, seph2, decay_divisor)
        
        # Calculate potential difference across the path
        potential_diff = abs(potentials[seph1] - potentials[seph2])
        
        # Flow intensity = potential difference * conductivity
        flow_intensity = potential_diff * conductivity
        path_flows.append(flow_intensity)
    
    # Step 4: Use standard deviation to determine relative thresholds
    if len(path_flows) > 1:
        mean_flow = sum(path_flows) / len(path_flows)
        variance = sum((f - mean_flow) ** 2 for f in path_flows) / len(path_flows)
        std_dev = math.sqrt(variance) if variance > 0 else 1.0
        threshold = std_dev * 0.8  # Adjust sensitivity
    else:
        mean_flow = path_flows[0] if path_flows else 0.0
        threshold = 10.0  # Default threshold for single readings
    
    # Step 5: Assign states based on relative flow intensity
    for i, (path_name, flow_intensity) in enumerate(zip(chosen_paths, path_flows)):
        if flow_intensity > (mean_flow + threshold):
            state = 'Excessive'  # High energy flow - path is overcharged
        elif flow_intensity < (mean_flow - threshold):
            state = 'Deficient'  # Low energy flow - path is blocked or weak
        else:
            state = 'Normal'  # Balanced flow
        
        result.append((path_name, state))
    
    return result

# === MAIN LOGIC ===
def main():
    parser = argparse.ArgumentParser(
        description="Kabbalistic readings based on cryptographic hashing.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-q', '--query', required=True, help='Your sacred query.')
    parser.add_argument(
        '-r', '--reading-type',
        choices=['1', '3', '10', '4'],
        default='3',
        help="""Type of reading:
1: Single Sephirah & Path
3: Mind/Heart/Body Pillar Reading (default)
10: Full Tree of Life
4: Four Worlds Reading"""
    )
    parser.add_argument(
        '-p', '--paths',
        type=int,
        help=f"Number of paths to draw (0-{NUM_PATHS}). If not specified, a number is determined from the query."
    )
    args = parser.parse_args()

    question = args.query
    revelation_choice = args.reading_type

    # Create a cryptographically secure, non-deterministic seed
    seed = urandom(ProtectiveHasher.HASH_LENGTH)
    
    auth_hash = ProtectiveHasher.derive_protected_bytes(seed, b"kabbalah-auth")
    auth_string = auth_hash.hex()[:8].upper()

    # Select the World (Atmospheric Filter)
    selected_world = select_world(seed, question)
    
    console.print(f"[bold purple]Kabbalistic Divination for:[/bold purple] '{question}'")
    console.print(f"[dim]Entropy Source:[/dim] os.urandom")
    console.print(f"[dim]Auth:[/dim] [bold green]{auth_string}[/bold green]")
    console.print(f"[bold cyan]World:[/bold cyan] {selected_world['name']}")
    console.print(f"[dim]{selected_world['description']}[/dim]")


    # Determine sephirot count
    if revelation_choice in ['1', '3']:
        sephirot_count = int(revelation_choice)
        revealed_sephirot_with_states = get_sephirot_reading(seed, question, sephirot_count, selected_world)
    else: # '10' or '4'
        sephirot_count = 10
        revealed_sephirot_with_states = get_sephirot_reading(seed, question, 10, selected_world)

    # Determine path count
    if args.paths is not None:
        path_count = args.paths
        if not (0 <= path_count <= NUM_PATHS):
            console.print(f"[red]Error: Path count must be between 0 and {NUM_PATHS}.[/red]")
            return
    else:
        # If not specified, derive it from the query
        path_count = (hash_for_int(seed, question, "path-count-salt") % (NUM_PATHS // 2)) + 1

    revealed_paths_with_states = get_paths_reading(seed, question, path_count, selected_world)

    # --- Display Results ---
    console.print("[bold magenta]The Revealed Sephiroth:[/bold magenta]")
    if revelation_choice == '4':
        world_readings = {world_name: [] for world_name in worlds}
        for sephirah, state in revealed_sephirot_with_states:
            for world_name, sephirot_in_world in worlds.items():
                if sephirah in sephirot_in_world:
                    world_readings[world_name].append(f"{sephirah} ('{state}')" if state != 'Normal' else sephirah)
        for world_name, readings in world_readings.items():
            console.print(f"[bold]{world_name} World:[/bold] {', '.join(readings)}")
    else:
        for i, (s_name, state) in enumerate(revealed_sephirot_with_states):
            state_str = f" ([red]{state}[/red])" if state != 'Normal' else ""
            console.print(f"[bold]{i+1}. {s_name}[/bold]{state_str}")

    if revealed_paths_with_states:
        console.print(f"[bold magenta]The Revealed Paths:[/bold magenta]")
        for i, (p_name, state) in enumerate(revealed_paths_with_states):
            state_str = f" ([red]{state}[/red])" if state != 'Normal' else ""
            console.print(f"[bold]{i+1}. {p_name}[/bold]{state_str}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("[bold red]⏹️ Revelation canceled.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
