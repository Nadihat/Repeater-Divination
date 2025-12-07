#!/usr/bin/env python3
"""
KABBALAH4.py
Kabbalistic readings based on cryptographic hashing.

This version provides non-deterministic, non-interactive readings based on a user's query,
inspired by the automatic nature of I-CHING3.py. It uses a strong key derivation
function (PBKDF2) to ensure that the results are both repeatable for a given
query and cryptographically secure.

Usage:
    python3 KABBALAH4.py -q "Your question here" [options]

Options:
    -r, --reading-type [1|3|10|4]  Selects the type of reading. (Default: 3)
    -p, --paths N                  Specify the number of paths to draw. (Default: derived from query)
"""

import hashlib
import sys
import argparse
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

# === HASHING ENGINE ===
class ProtectiveHasher:
    PROTECTION_ITERATIONS = 888_888
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

def hash_for_int(seed: bytes, salt: str = "") -> int:
    salt_bytes = salt.encode("utf-8")
    hashed_bytes = ProtectiveHasher.derive_protected_bytes(seed, salt_bytes)
    return int.from_bytes(hashed_bytes, 'big')

# === AUTOMATIC READING LOGIC ===
def get_sephirot_reading(seed: bytes, count: int) -> List[Tuple[str, str]]:
    """
    Deterministically selects Sephirot and their states based on the question.
    If count is 10, it gets the state for all Sephirot.
    Otherwise, it selects 'count' unique Sephirot and their states.
    """
    states = ['Normal', 'Deficient', 'Excessive']
    
    if count >= 10:
        chosen_names = sephirot_names
    else:
        available_sephirot = sephirot_names.copy()
        chosen_names = []
        for i in range(count):
            salt = f"sephirah-name-{i}"
            index = hash_for_int(seed, salt) % len(available_sephirot)
            chosen_names.append(available_sephirot.pop(index))

    result = []
    for i, name in enumerate(chosen_names):
        salt = f"sephirah-state-{name}-{i}"
        # Determine state based on desired probabilities: Normal (85%), Deficient (7.5%), Excessive (7.5%)
        hash_value = hash_for_int(seed, salt)
        # Use a large number for modulo to ensure fine-grained probability distribution
        # 1000 provides 0.1% granularity, so 7.5% = 75, 85% = 850
        prob_roll = hash_value % 1000

        if prob_roll < 75:  # 0-74 (7.5% chance)
            chosen_state = 'Deficient'
        elif prob_roll < 150: # 75-149 (7.5% chance)
            chosen_state = 'Excessive'
        else: # 150-999 (85% chance)
            chosen_state = 'Normal'
        
        result.append((name, chosen_state))
        
    return result

def get_paths_reading(seed: bytes, count: int) -> List[str]:
    """Deterministically selects Paths based on the question."""
    if count == 0:
        return []
    
    available_paths = paths.copy()
    chosen_paths = []
    for i in range(count):
        salt = f"path-{i}"
        index = hash_for_int(seed, salt) % len(available_paths)
        chosen_paths.append(available_paths.pop(index))
    return chosen_paths

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

    # Create a non-deterministic seed
    timestamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
    seed_material = f"{question}|{timestamp}".encode('utf-8')
    seed = hashlib.sha256(seed_material).digest()
    
    auth_hash = ProtectiveHasher.derive_protected_bytes(seed, b"kabbalah-auth")
    auth_string = auth_hash.hex()[:8].upper()


    console.print(f"[bold purple]Kabbalistic Divination for:[/bold purple] '{question}'")
    console.print(f"[dim]Time:[/dim] {timestamp}")
    console.print(f"[dim]Auth:[/dim] [bold green]{auth_string}[/bold green]")


    # Determine sephirot count
    if revelation_choice in ['1', '3']:
        sephirot_count = int(revelation_choice)
        revealed_sephirot_with_states = get_sephirot_reading(seed, sephirot_count)
    else: # '10' or '4'
        sephirot_count = 10
        revealed_sephirot_with_states = get_sephirot_reading(seed, 10)

    # Determine path count
    if args.paths is not None:
        path_count = args.paths
        if not (0 <= path_count <= NUM_PATHS):
            console.print(f"[red]Error: Path count must be between 0 and {NUM_PATHS}.[/red]")
            return
    else:
        # If not specified, derive it from the query
        path_count = (hash_for_int(seed, "path-count-salt") % (NUM_PATHS // 2)) + 1

    revealed_paths = get_paths_reading(seed, path_count)

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

    if revealed_paths:
        console.print(f"[bold magenta]The Revealed Paths:[/bold magenta]")
        for i, p_name in enumerate(revealed_paths):
            console.print(f"[bold]{i+1}. {p_name}[/bold]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("[bold red]⏹️ Revelation canceled.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
