#!/usr/bin/env python3
"""
KABBALAH2.py
Interactive Kabbalistic readings based on cryptographic hashing.
"""

import hashlib
import requests
import os
import sys
import argparse
import random
from typing import List, Tuple, Dict
from rich import print
from rich.console import Console

# === CONFIGURATION ===
DEFAULT_MODEL = "x-ai/grok-3-beta"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
HASH_PREFIX_LEN = 8
NUM_PATHS = 22 # The 22 Paths of the Tree of Life

console = Console()

# === KABBALISTIC DATA ===
sephirot_names = [
    'Keter (Crown)', 'Chokmah (Wisdom)', 'Binah (Understanding)', 'Chesed (Mercy)',
    'Gevurah (Strength)', 'Tiferet (Beauty)', 'Netzach (Victory)', 'Hod (Splendor)',
    'Yesod (Foundation)', 'Malkuth (Kingdom)'
]

# Generate the full list of 30 Sephiroth states
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

# === INTERPRETATION REQUEST ===
def interpret_revelation(question: str, sephirot_list: List[Tuple[str, str]], path_list: List[str], model: str, reading_info: str = "") -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return (
            "[red]❌ OPENROUTER_API_KEY environment variable not set.[/red]\n"
            "[yellow]💡 Tip: Get a key from https://openrouter.ai and set it.[/yellow]\n"
            "   Linux/macOS: export OPENROUTER_API_KEY='your-key-here'\n"
            "   Windows: setx OPENROUTER_API_KEY your-key-here"
        )

    sephirot_text = ""
    if "Four Worlds" in reading_info:
        world_readings = {world_name: [] for world_name in worlds}
        for sephirah, state in sephirot_list:
            for world_name, sephirot_in_world in worlds.items():
                if sephirah in sephirot_in_world:
                    world_readings[world_name].append(f"{sephirah} ({state})" if state != 'Normal' else sephirah)
                    break
        sephirot_text_parts = [f"[bold]{world_name} World:[/bold] {', '.join(readings)}" for world_name, readings in world_readings.items()]
        sephirot_text = "\n".join(sephirot_text_parts)
    elif len(sephirot_list) == 10:
        tree_of_life_map = {s.split(' ')[0]: f"{s} ({st})" if st != 'Normal' else s for s, st in sephirot_list}
        positions = [
            f"1. Keter (Crown): {tree_of_life_map.get('Keter', 'Not Revealed')}",
            f"2. Chokmah (Wisdom): {tree_of_life_map.get('Chokmah', 'Not Revealed')}",
            f"3. Binah (Understanding): {tree_of_life_map.get('Binah', 'Not Revealed')}",
            f"4. Chesed (Mercy): {tree_of_life_map.get('Chesed', 'Not Revealed')}",
            f"5. Gevurah (Strength): {tree_of_life_map.get('Gevurah', 'Not Revealed')}",
            f"6. Tiferet (Beauty): {tree_of_life_map.get('Tiferet', 'Not Revealed')}",
            f"7. Netzach (Victory): {tree_of_life_map.get('Netzach', 'Not Revealed')}",
            f"8. Hod (Splendor): {tree_of_life_map.get('Hod', 'Not Revealed')}",
            f"9. Yesod (Foundation): {tree_of_life_map.get('Yesod', 'Not Revealed')}",
            f"10. Malkuth (Kingdom): {tree_of_life_map.get('Malkuth', 'Not Revealed')}"
        ]
        sephirot_text = "\n".join(positions)
    else:
        sephirot_text = ", ".join([f"{s} ({st})" if st != 'Normal' else s for s, st in sephirot_list])

    path_text = ", ".join(path_list)

    system_prompt = (
        "You are an Anthro sage giving a spiritual Kabbalistic reading... (rest of prompt)"
    )
    user_prompt = (
        f"The question is: '{question}'\n\n"
        f"{reading_info}\n\n"
        f"The following Sephirot were revealed from the Tree of Life:\n{sephirot_text}\n\n"
        f"The following Paths were revealed:\n{path_text}"
    )

    payload = { "model": model, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}] }
    headers = { "Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "HTTP-Referer": "https://github.com/reden/kabbalah", "X-Title": "OpenRouter Kabbalah" }
    console.print("\n[bold blue]Consulting the Ein Sof...[/bold blue]")
    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=300)
        response.raise_for_status()
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "No response from LLM.")
    except Exception as e:
        return f"[red]Error: {e}[/red]"

# === MAIN LOGIC ===
def get_user_choices(available_hashes: List[str], num_choices: int, item_name: str) -> List[str]:
    chosen_hashes = []
    while len(chosen_hashes) < num_choices:
        console.print(f"\n[bold]Available {item_name} Hashes:[/bold]")
        cols = 4
        for i in range(0, len(available_hashes), cols):
            console.print("  ".join(f"[{h}]" for h in available_hashes[i:i + cols]))
        choices_str = console.input(f"\nEnter {num_choices} {item_name} hash prefix(es) (3+ chars), separated by commas: ").strip()
        choices = [c.strip().lower() for c in choices_str.split(',') if c.strip()]
        if len(choices) != num_choices:
            console.print(f"[red]Please enter exactly {num_choices} comma-separated hashes.[/red]")
            continue
        valid_choices = True
        temp_chosen = []
        for choice in choices:
            if len(choice) < 3: console.print(f"[red]Error: Hash prefix '{choice}' must be at least 3 characters long.[/red]"); valid_choices = False; break
            matches = [h for h in available_hashes if h.startswith(choice)]
            if len(matches) == 1: temp_chosen.append(matches[0])
            elif len(matches) > 1: console.print(f"[red]Ambiguous choice '{choice}'.[/red]"); valid_choices = False; break
            else: console.print(f"[red]Invalid choice '{choice}'.[/red]"); valid_choices = False; break
        if valid_choices: chosen_hashes = temp_chosen; break
    return chosen_hashes

def main():
    parser = argparse.ArgumentParser(description="Interactive Kabbalistic readings.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help=f"Model to use. Default: '{DEFAULT_MODEL}'")
    args = parser.parse_args()

    console.print("[bold purple]Welcome to Interactive Anthro Kabbalah[/bold purple] 🌳")
    console.print(f"[dim]Using model: {args.model}[/dim]")
    question = console.input("[bold yellow]Inscribe your sacred query to generate the hashes[/bold yellow]: ").strip()
    if not question: console.print("[red]A question is required.[/red]"); return

    console.print("\n[bold]Choose your revelation:[/bold]")
    console.print("[green]1[/green]: Single Sephirah & Path")
    console.print("[green]3[/green]: Pillar Reading (3 Sephirot, 3 Paths)")
    console.print("[green]10[/green]: Full Tree of Life (10 Sephirot, 5 Paths)")
    console.print("[green]V[/green]: Full Tree with Variable Paths")
    console.print("\n--- Horizontal Readings ---")
    console.print("[green]A[/green]: Archetypal World")
    console.print("[green]C[/green]: Creative World")
    console.print("[green]F[/green]: Formative World")
    console.print("[green]M[/green]: Material World")
    console.print("[green]4[/green]: Four Worlds Reading")
    revelation_choice = console.input("Your choice: ").strip().upper()

    sephirot_count, path_count = 0, 0
    reading_info = ""
    sephirot_pool_source = sephirot_with_states # Default to all 30 states

    if revelation_choice in ['1', '3', '10']:
        sephirot_count = int(revelation_choice)
        path_count = {1: 1, 3: 3, 10: 5}[sephirot_count]
    elif revelation_choice == 'V':
        sephirot_count = 10
        path_count = (hash_question_for_int(question, "path-count-salt") % NUM_PATHS) + 1
    elif revelation_choice in ['A', 'C', 'F', 'M']:
        world_map = {'A': "Archetypal", 'C': "Creative", 'F': "Formative", 'M': "Material"}
        world_name = world_map[revelation_choice]
        reading_info = f"This is a horizontal reading of the {world_name} World."
        world_sephirot_names = worlds[world_name]
        sephirot_pool_source = [s for s in sephirot_with_states if any(ws_name in s for ws_name in world_sephirot_names)]
        sephirot_count = len(world_sephirot_names) # Draw one for each sephirah in the world
        path_count = sephirot_count
    elif revelation_choice == '4':
        reading_info = "This is a Four Worlds reading."
        sephirot_pool_source = sephirot_with_states
        sephirot_count = len(sephirot_names) # Draw one for each of the 10 sephirot types
        path_count = 4
    else:
        console.print("[red]Invalid choice. Please run the script again.[/red]"); return

    # --- Hash Pool Generation ---
    console.print("\n[cyan]Generating protected hash pools...[/cyan]")
    sephirot_pool = prepare_interactive_pool(question, sephirot_pool_source, "sephirah")
    paths_pool = prepare_interactive_pool(question, paths, "path")
    
    available_sephirot_hashes = list(sephirot_pool.keys())
    available_path_hashes = list(paths_pool.keys())

    # --- User Selection ---
    chosen_sephirot_hashes = get_user_choices(available_sephirot_hashes, sephirot_count, "Sephirah")
    revealed_sephirot_with_states: List[Tuple[str, str]] = []
    for h in chosen_sephirot_hashes:
        selected_item = sephirot_pool[h]
        s_name, state = selected_item.rsplit(' - ', 1)
        revealed_sephirot_with_states.append((s_name, state))

    chosen_path_hashes = get_user_choices(available_path_hashes, path_count, "Path")
    revealed_paths = [paths_pool[h] for h in chosen_path_hashes]

    # --- Display Results ---
    console.print("\n[bold magenta]The Revealed Sephiroth:[/bold magenta]")
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

    console.print(f"\n[bold magenta]The Revealed Paths:[/bold magenta]")
    for i, p_name in enumerate(revealed_paths):
        console.print(f"[bold]{i+1}. {p_name}[/bold]")

    # --- Interpretation ---
    interpretation = interpret_revelation(question, revealed_sephirot_with_states, revealed_paths, args.model, reading_info)
    console.print(f"\n[italic green]{interpretation}[/italic green]\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]⏹️ Revelation canceled.[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred: {e}[/bold red]")