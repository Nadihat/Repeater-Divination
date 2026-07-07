#!/usr/bin/env python3
"""
pure_kabbalah.py — Kabbalistic divination from unbiased atmospheric entropy.
Every decision is one random byte → one outcome. No averaging. No flow models.
No relative thresholds. The atmosphere speaks directly.
"""

import sys
import argparse
import urllib.request
import hashlib
from typing import List, Tuple, Optional
from rich.console import Console

console = Console()
NUM_PATHS = 22

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

worlds_grouping = {
    "Archetypal": ['Keter (Crown)', 'Chokmah (Wisdom)', 'Binah (Understanding)'],
    "Creative": ['Chesed (Mercy)', 'Gevurah (Strength)', 'Tiferet (Beauty)'],
    "Formative": ['Netzach (Victory)', 'Hod (Splendor)', 'Yesod (Foundation)'],
    "Material": ['Malkuth (Kingdom)']
}

# --- DIAGNOSTIC METRICS ---

SEVEN_WORLDS = {
    "Assiah": {"name": "Assiah (Earth/Action)", "description": "High Density, High Resistance — Energy flows like lava", "weight": 30},
    "Yetzirah": {"name": "Yetzirah (Water/Formation)", "description": "High Sensitivity, Swirling Flow — Energy flows like a river", "weight": 28},
    "Briah": {"name": "Briah (Air/Creation)", "description": "High Intelligence, Fast Movement — Energy flows like sound", "weight": 22},
    "Atziluth": {"name": "Atziluth (Fire/Emanation)", "description": "High Potential, Low Resistance — Energy flows like light", "weight": 14},
    "Ain Sof Aur": {"name": "Ain Sof Aur (Limitless Light)", "description": "The first radiance before form", "weight": 3},
    "Ain Sof": {"name": "Ain Sof (The Limitless)", "description": "Boundlessness without quality", "weight": 2},
    "Ain": {"name": "Ain (No-Thing)", "description": "The Absolute Void", "weight": 1}
}

SOUL_LEVELS = {
    "Nefesh": {"name": "Nefesh (The Animal Soul)", "description": "Driven by physical survival, habits, health, and materiality.", "weight": 40},
    "Ruach": {"name": "Ruach (The Wind/Spirit)", "description": "Driven by emotions, relationships, and moral friction.", "weight": 35},
    "Neshamah": {"name": "Neshamah (The Breath)", "description": "Driven by higher intellect, life purpose, and spiritual clarity.", "weight": 15},
    "Chayah": {"name": "Chayah (The Living Force)", "description": "Driven by systemic forces and the collective unconscious.", "weight": 8},
    "Yechidah": {"name": "Yechidah (The Singularity)", "description": "Driven by absolute unity; the human ego dissolves completely.", "weight": 2}
}

PARTZUFIM = {
    "Zeir Anpin": {"name": "Zeir Anpin (The Short Face)", "description": "High volatility: impulsive, emotional, short-term conflict and resolution.", "weight": 40},
    "Nukva": {"name": "Nukva (The Bride/Daughter)", "description": "Pure receptivity: grounding, receiving, and materializing the outcome.", "weight": 30},
    "Imma": {"name": "Imma (The Mother)", "description": "Gestation: processing, analyzing, and setting hard boundaries.", "weight": 15},
    "Abba": {"name": "Abba (The Father)", "description": "The Flash: sudden inspiration, raw unformed potential.", "weight": 10},
    "Arik Anpin": {"name": "Arik Anpin (The Long Face)", "description": "Macro-scale: infinite patience, absolute mercy, massive timing over years.", "weight": 5}
}

VEILS = {"Ain Sof Aur", "Ain Sof", "Ain"}


# === ENTROPY SOURCE ===

def get_random_org_pool(num_integers: int = 256) -> List[int]:
    url = (f"https://www.random.org/integers/?num={num_integers}"
           f"&min=0&max=255&col=1&base=10&format=plain&rnd=new")
    headers = {'User-Agent': 'Kabbalah-Divination/11.0'}
    req = urllib.request.Request(url, headers=headers)
    try:
        response = urllib.request.urlopen(req)
        data = response.read().decode('utf-8').strip()
        if data.startswith("Error:"):
            print(f"Random.org error: {data}", file=sys.stderr)
            sys.exit(1)
        return [int(x) for x in data.split('\n') if x.strip()]
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: Random.org unavailable.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Network error: {e}", file=sys.stderr)
        sys.exit(1)


class EntropyPool:
    def __init__(self, initial_pool: List[int]):
        self.pool = initial_pool
        self.consumed = 0

    def draw(self) -> int:
        if not self.pool:
            console.print("[dim]Fetching additional entropy...[/dim]")
            self.pool = get_random_org_pool(256)
        self.consumed += 1
        return self.pool.pop()

    def draw_uniform(self, n: int) -> int:
        if n <= 0:
            raise ValueError("n must be positive")
        if n == 1:
            return 0
        limit = (256 // n) * n 
        while True:
            val = self.draw()
            if val < limit:
                return val % n

    def draw_state(self) -> str:
        while True:
            val = self.draw()
            if val < 252:
                return ("Excessive", "Balanced", "Deficient")[val % 3]

    def draw_weighted(self, keys: List[str], weights: List[int]) -> str:
        total = sum(weights)
        roll = self.draw_uniform(total)
        cumulative = 0
        for key, weight in zip(keys, weights):
            cumulative += weight
            if roll < cumulative:
                return key
        return keys[-1]

    def draw_sample(self, population: list, k: int) -> list:
        pool_copy = population.copy()
        result = []
        for i in range(k):
            j = self.draw_uniform(len(pool_copy))
            result.append(pool_copy.pop(j))
        return result


# === READING LOGIC ===

def format_state(state: str) -> str:
    if state == "Balanced":
        return f"([green]{state}[/green])"
    elif state == "Excessive":
        return f"([bold red]{state}[/bold red])"
    else:
        return f"([blue]{state}[/blue])"

def check_daat(pool: EntropyPool) -> Optional[Tuple[str, str]]:
    roll = pool.draw_uniform(100)
    if roll < 15:
        polarity_byte = pool.draw()
        state = "Excessive" if polarity_byte % 2 == 0 else "Deficient"
        return ("Da'at (Knowledge)", state)
    return None

def get_sephirot_reading(pool: EntropyPool, count: int) -> List[Tuple[str, str]]:
    result = []
    daat = check_daat(pool)
    if daat:
        result.append(daat)
        if daat[1] == "Excessive":
            console.print("[bold yellow]⚡ REVELATION: The Abyss (Da'at) is Bridged! ⚡[/bold yellow]")
        else:
            console.print("[dim]The Abyss is Silent (Deficient Da'at)[/dim]")

    if count >= 10:
        chosen = sephirot_names.copy()
    else:
        chosen = pool.draw_sample(sephirot_names, count)

    for name in chosen:
        state = pool.draw_state()
        result.append((name, state))

    return result

def get_paths_reading(pool: EntropyPool, count: int) -> List[Tuple[str, str]]:
    if count == 0:
        return []
    safe_count = min(count, len(paths))
    chosen = pool.draw_sample(paths, safe_count)
    result = []
    for path_name in chosen:
        state = pool.draw_state()
        result.append((path_name, state))
    return result

def handle_veil_reading(world_key: str, pool: EntropyPool):
    if world_key == "Ain":
        console.print("\n[bold white on black]  ∅  THE VOID  ∅  [/bold white on black]")
        console.print("[dim]Your question returns to silence. There is nothing to read.[/dim]")
    elif world_key == "Ain Sof":
        console.print("\n[bold white]  ∞  THE LIMITLESS  ∞  [/bold white]")
        console.print("[dim]The situation is unbounded. No fixed outcome exists.[/dim]")
    elif world_key == "Ain Sof Aur":
        console.print("\n[bold yellow]  ✦  LIMITLESS LIGHT  ✦  [/bold yellow]")
        console.print("[dim]Potential coalesces but has not taken form.[/dim]")
        state = pool.draw_state()
        chosen = pool.draw_sample(sephirot_names, 1)
        console.print(f"\n[bold magenta]A single echo from the Light:[/bold magenta]")
        console.print(f"  [bold]{chosen[0]}[/bold] {format_state(state)}\n")


# === MAIN ===

def main():
    parser = argparse.ArgumentParser(
        description="Kabbalistic divination from unbiased atmospheric entropy.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-q', '--query', required=True, help='Your sacred query.')
    parser.add_argument(
        '-r', '--reading-type',
        choices=['0', '1', '3', '10', '4'],
        default='3',
        help=("Type of reading:\n"
              "0: Automatic\n"
              "1: Single Sephirah\n"
              "3: Three Pillars\n"
              "10: Full Tree of Life\n"
              "4: Four Worlds Reading")
    )
    parser.add_argument('-p', '--paths', type=int, help=f"Number of paths (0-{NUM_PATHS}). Default: random.")
    args = parser.parse_args()

    pool = EntropyPool(get_random_org_pool(256))

    auth_bytes = bytes([pool.draw() for _ in range(32)])
    auth_string = hashlib.sha256(auth_bytes).hexdigest()[:8].upper()

    # --- CORE DIAGNOSTIC THROWS ---
    world_key = pool.draw_weighted(list(SEVEN_WORLDS.keys()), [SEVEN_WORLDS[k]["weight"] for k in SEVEN_WORLDS])
    soul_key = pool.draw_weighted(list(SOUL_LEVELS.keys()), [SOUL_LEVELS[k]["weight"] for k in SOUL_LEVELS])
    partzuf_key = pool.draw_weighted(list(PARTZUFIM.keys()), [PARTZUFIM[k]["weight"] for k in PARTZUFIM])

    sel_world = SEVEN_WORLDS[world_key]
    sel_soul = SOUL_LEVELS[soul_key]
    sel_partzuf = PARTZUFIM[partzuf_key]

    # --- PRINT HEADER ---
    console.print(f"\n[bold purple]Kabbalistic Divination for:[/bold purple] '{args.query}'")
    console.print(f"[dim]Auth Hash:[/dim] [bold green]{auth_string}[/bold green]\n")

    console.print(f"[bold cyan]World:[/bold cyan] {sel_world['name']}")
    console.print(f"[dim]{sel_world['description']}[/dim]")
    
    if world_key not in VEILS:
        console.print(f"[bold yellow]Soul Origin:[/bold yellow] {sel_soul['name']}")
        console.print(f"[dim]{sel_soul['description']}[/dim]")
        
        console.print(f"[bold blue]Active Partzuf:[/bold blue] {sel_partzuf['name']}")
        console.print(f"[dim]{sel_partzuf['description']}[/dim]")

    if world_key in VEILS:
        handle_veil_reading(world_key, pool)
        return

    # --- GET NODES ---
    sephirot_count = 10 if args.reading_type in ('4', '10') else (pool.draw_uniform(10) + 1 if args.reading_type == '0' else int(args.reading_type))
    revealed_sephirot = get_sephirot_reading(pool, sephirot_count)
    path_count = args.paths if args.paths is not None else pool.draw_uniform(NUM_PATHS + 1)
    revealed_paths = get_paths_reading(pool, path_count)

    # --- DISPLAY RESULTS ---
    console.print("\n[bold magenta]The Revealed Sephiroth:[/bold magenta]")

    if args.reading_type == '4':
        world_readings = {wn: [] for wn in worlds_grouping}
        daat_str = None
        for sephirah, state in revealed_sephirot:
            if "Da'at" in sephirah:
                daat_str = f"{sephirah} {format_state(state)}"
                continue
            for wn, s_list in worlds_grouping.items():
                if sephirah in s_list:
                    world_readings[wn].append(f"{sephirah} {format_state(state)}")
        for wn, readings in world_readings.items():
            if readings:
                console.print(f"  [bold]{wn} World:[/bold] {', '.join(readings)}")
        if daat_str:
            console.print(f"  [bold yellow]The Abyss:[/bold yellow] {daat_str}")
    else:
        for i, (name, state) in enumerate(revealed_sephirot):
            console.print(f"  [bold]{i+1}. {name}[/bold] {format_state(state)}")

    if revealed_paths:
        console.print(f"\n[bold magenta]The Revealed Paths:[/bold magenta]")
        for i, (name, state) in enumerate(revealed_paths):
            console.print(f"  [bold]{i+1}. {name}[/bold] {format_state(state)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]⏹️ Revelation canceled.[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred: {e}[/bold red]")
