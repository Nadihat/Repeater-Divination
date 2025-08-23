#!/usr/bin/env python3
"""
KABBALAH2.py
Interactive Kabbalistic readings based on cryptographic hashing.
"""

import hashlib
import os
import sys
import argparse
import random
from typing import List, Tuple, Dict
from rich import print
from rich.console import Console
from rich.table import Table

# === CONFIGURATION ===
HASH_PREFIX_LEN = 10
NUM_PATHS = 22 # The 22 Paths of the Tree of Life

console = Console()

# === KABBALISTIC DATA ===
sephirot_names = [
    'Keter (Crown)', 'Chokmah (Wisdom)', 'Binah (Understanding)', 'Chesed (Mercy)',
    'Gevurah (Strength)', 'Tiferet (Beauty)', 'Netzach (Victory)', 'Hod (Splendor)',
    'Yesod (Foundation)', 'Malkuth (Kingdom)'
]

sephirot_with_states = [
    f"{name} - {state}"
    for name in sephirot_names
    for state in ['Normal', 'Deficient', 'Excessive']
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

def hash_question_for_int(question: str, salt: str = "") -> int:
    base_bytes = hashlib.sha256(question.encode("utf-8")).digest()
    salt_bytes = salt.encode("utf-8")
    hashed_bytes = ProtectiveHasher.derive_protected_bytes(base_bytes, salt_bytes)
    return int.from_bytes(hashed_bytes, 'big')

def prepare_interactive_pool(question: str, items: List[str], salt_prefix: str) -> Dict[str, str]:
    # ... (This function remains unchanged)
    base_seed = hashlib.sha256(question.encode("utf-8")).digest()
    rng = random.Random(base_seed)
    indices = list(range(len(items)))
    rng.shuffle(indices)
    interactive_pool: Dict[str, str] = {}
    total_hashes = len(indices)
    for i, item_index in enumerate(indices):
        print(f"Calculating {salt_prefix} hash {i+1}/{total_hashes}...", end='\r', file=sys.stderr)
        salt = f"{salt_prefix}-{i}".encode("utf-8")
        protected_digest = ProtectiveHasher.derive_protected_bytes(base_seed, salt)
        hash_hex = protected_digest.hex()
        interactive_pool[hash_hex[:HASH_PREFIX_LEN]] = items[item_index]
    print(file=sys.stderr)
    return interactive_pool



# === MAIN LOGIC ===
def get_user_choices(pool: Dict[str, str], num_choices: int, item_name: str) -> List[str]:
    # ... (This function remains unchanged)
    available_hashes = list(pool.keys())
    chosen_hashes = []
    while True:
        console.print(f"\n[bold]Available {item_name} Hashes:[/bold]")
        table = Table.grid(expand=True)
        cols = 4
        for _ in range(cols):
            table.add_column()

        for i in range(0, len(available_hashes), cols):
            row = [f"[{h}]" for h in available_hashes[i:i+cols]]
            table.add_row(*row)
        console.print(table)
        choices_str = console.input(f"\nEnter {num_choices} {item_name} hash prefix(es) (3+ chars), separated by commas: ").strip()
        choices = [c.strip().lower() for c in choices_str.split(',') if c.strip()]
        if len(choices) != num_choices:
            console.print(f"[red]Please enter exactly {num_choices} hashes.[/red]")
            continue
        valid_choices = True
        temp_chosen_hashes = []
        temp_chosen_base_names = []
        for choice in choices:
            if len(choice) < 3:
                console.print(f"[red]Error: Hash prefix '{choice}' must be at least 3 characters long.[/red]")
                valid_choices = False; break
            matches = [h for h in available_hashes if h.startswith(choice)]
            if len(matches) == 1:
                chosen_hash = matches[0]
                temp_chosen_hashes.append(chosen_hash)
                if item_name == "Sephirah":
                    base_name = pool[chosen_hash].split(' - ')[0]
                    if base_name in temp_chosen_base_names:
                        console.print(f"[red]Error: You have selected multiple states of '{base_name}'.[/red]")
                        valid_choices = False; break
                    temp_chosen_base_names.append(base_name)
            elif len(matches) > 1:
                console.print(f"[red]Ambiguous choice '{choice}'.[/red]")
                valid_choices = False; break
            else:
                console.print(f"[red]Invalid choice '{choice}'.[/red]")
                valid_choices = False; break
        if valid_choices:
            chosen_hashes = temp_chosen_hashes
            break
    return chosen_hashes

def main():
    parser = argparse.ArgumentParser(description="Interactive Kabbalistic readings.", formatter_class=argparse.RawTextHelpFormatter)
    args = parser.parse_args()

    console.print("[bold purple]Welcome to Interactive Anthro Kabbalah[/bold purple] 🌳")
    question = console.input("[bold yellow]Inscribe your sacred query to generate the hashes[/bold yellow]: ").strip()
    if not question: console.print("[red]A question is required.[/red]"); return

    # --- Hash Pool Generation ---
    console.print("\n[cyan]Generating protected hash pools for all 30 Sephiroth and 22 Paths...[/cyan]")
    sephirot_pool = prepare_interactive_pool(question, sephirot_with_states, "sephirah")
    paths_pool = prepare_interactive_pool(question, paths, "path")

    console.print("\n[bold]Choose your revelation:[/bold]")
    console.print("[green]1[/green]: Single Sephirah & Path")
    console.print("[green]3[/green]: Mind/Heart/Body Pillar Reading")
    console.print("[green]10[/green]: Full Tree of Life")
    console.print("[green]4[/green]: Four Worlds Reading")
    revelation_choice = console.input("Your choice: ").strip().upper()

    sephirot_count = 0
    reading_info = ""
    
    if revelation_choice in ['1', '3', '10']:
        sephirot_count = int(revelation_choice)
    elif revelation_choice == '4':
        reading_info = "This is a Four Worlds reading."
        sephirot_count = len(sephirot_names)
    else:
        console.print("[red]Invalid choice. Please run the script again.[/red]"); return

    # --- Path Count ---
    recommended_paths = (hash_question_for_int(question, "path-count-salt") % (NUM_PATHS // 2)) + 1
    console.print(f"\n[bold]Recommendation of Path Numbers to Draw:[/bold] {recommended_paths}")
    try:
        path_count_str = console.input(f"How many paths to draw? (0 for none, Enter for recommendation): ").strip()
        path_count = int(path_count_str) if path_count_str else recommended_paths
        if not (0 <= path_count <= NUM_PATHS):
            console.print(f"[red]Please enter a number between 0 and {NUM_PATHS}.[/red]"); return
    except ValueError:
        console.print("[red]Invalid number.[/red]"); return

    # --- User Selection ---
    chosen_sephirot_hashes = get_user_choices(sephirot_pool, sephirot_count, "Sephirah")
    revealed_sephirot_with_states: List[Tuple[str, str]] = []
    for h in chosen_sephirot_hashes:
        selected_item = sephirot_pool[h]
        s_name, state = selected_item.rsplit(' - ', 1)
        revealed_sephirot_with_states.append((s_name, state))

    revealed_paths = []
    if path_count > 0:
        chosen_path_hashes = get_user_choices(paths_pool, path_count, "Path")
        revealed_paths = [paths_pool[h] for h in chosen_path_hashes]

    # --- Display Results ---
    console.print("\n[bold magenta]The Revealed Sephiroth:[/bold magenta]")
    # ... (Display logic remains the same)
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
        console.print(f"\n[bold magenta]The Revealed Paths:[/bold magenta]")
        for i, p_name in enumerate(revealed_paths):
            console.print(f"[bold]{i+1}. {p_name}[/bold]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]⏹️ Revelation canceled.[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred: {e}[/bold red]")