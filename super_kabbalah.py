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

# Seven Worlds — weighted by proximity to manifestation
SEVEN_WORLDS = {
    "Assiah": {
        "name": "Assiah (Earth/Action)",
        "description": "High Density, High Resistance — Energy flows like lava",
        "weight": 30
    },
    "Yetzirah": {
        "name": "Yetzirah (Water/Formation)",
        "description": "High Sensitivity, Swirling Flow — Energy flows like a river",
        "weight": 28
    },
    "Briah": {
        "name": "Briah (Air/Creation)",
        "description": "High Intelligence, Fast Movement — Energy flows like sound",
        "weight": 22
    },
    "Atziluth": {
        "name": "Atziluth (Fire/Emanation)",
        "description": "High Potential, Low Resistance — Energy flows like light",
        "weight": 14
    },
    "Ain Sof Aur": {
        "name": "Ain Sof Aur (אין סוף אור — Limitless Light)",
        "description": "The first radiance before form — potential coalesces at the edge of manifestation",
        "weight": 3
    },
    "Ain Sof": {
        "name": "Ain Sof (אין סוף — The Limitless)",
        "description": "Boundlessness without quality — no fixed outcome exists",
        "weight": 2
    },
    "Ain": {
        "name": "Ain (אין — No-Thing)",
        "description": "The Absolute Void — the question itself dissolves",
        "weight": 1
    }
}

VEILS = {"Ain Sof Aur", "Ain Sof", "Ain"}


# === ENTROPY SOURCE ===

def get_random_org_pool(num_integers: int = 256) -> List[int]:
    """Fetches true atmospheric randomness from Random.org."""
    url = (f"https://www.random.org/integers/?num={num_integers}"
           f"&min=0&max=255&col=1&base=10&format=plain&rnd=new")
    headers = {'User-Agent': 'Kabbalah-Divination/10.0'}
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
    """Manages a pool of true random bytes. Fetches more if exhausted."""

    def __init__(self, initial_pool: List[int]):
        self.pool = initial_pool
        self.consumed = 0

    def draw(self) -> int:
        """Draw one unbiased byte [0-255]."""
        if not self.pool:
            console.print("[dim]Fetching additional entropy...[/dim]")
            self.pool = get_random_org_pool(256)
        self.consumed += 1
        return self.pool.pop()

    def draw_uniform(self, n: int) -> int:
        """Draw a uniform integer in [0, n-1] using rejection sampling.
        
        Eliminates modulo bias completely.
        For n <= 256, finds the largest multiple of n that fits in [0,255]
        and rejects values above it.
        """
        if n <= 0:
            raise ValueError("n must be positive")
        if n == 1:
            return 0

        # Largest multiple of n that is <= 256
        limit = (256 // n) * n  # e.g., n=10 → limit=250

        while True:
            val = self.draw()
            if val < limit:
                return val % n

    def draw_state(self) -> str:
        """Draw one of three states with perfect uniformity.
        
        252 is the largest multiple of 3 ≤ 256.
        Values 252-255 are rejected (1.5% rejection rate).
        """
        while True:
            val = self.draw()
            if val < 252:
                return ("Excessive", "Balanced", "Deficient")[val % 3]

    def draw_weighted(self, keys: List[str], weights: List[int]) -> str:
        """Weighted selection using rejection sampling.
        
        No floating point. Pure integer arithmetic on random bytes.
        """
        total = sum(weights)
        roll = self.draw_uniform(total)

        cumulative = 0
        for key, weight in zip(keys, weights):
            cumulative += weight
            if roll < cumulative:
                return key

        return keys[-1]  # Safety fallback

    def draw_sample(self, population: list, k: int) -> list:
        """Draw k unique items from population using Fisher-Yates on random bytes."""
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
    """Da'at: 15% chance of appearing. If it does, 50/50 Excessive/Deficient.
    
    One byte for the check (rejection-sampled to [0,99]).
    One byte for the polarity if triggered.
    """
    roll = pool.draw_uniform(100)  # [0, 99]
    if roll < 15:
        polarity_byte = pool.draw()
        state = "Excessive" if polarity_byte % 2 == 0 else "Deficient"
        return ("Da'at (Knowledge)", state)
    return None


def get_sephirot_reading(pool: EntropyPool, count: int) -> List[Tuple[str, str]]:
    """Select Sephirot and assign states. One byte per state, no transforms."""
    result = []

    # Check Da'at
    daat = check_daat(pool)
    if daat:
        result.append(daat)
        if daat[1] == "Excessive":
            console.print("[bold yellow]⚡ REVELATION: The Abyss (Da'at) is Bridged! ⚡[/bold yellow]")
        else:
            console.print("[dim]The Abyss is Silent (Deficient Da'at)[/dim]")

    # Select Sephirot
    if count >= 10:
        chosen = sephirot_names.copy()
    else:
        chosen = pool.draw_sample(sephirot_names, count)

    # One byte → one state, no intermediate math
    for name in chosen:
        state = pool.draw_state()
        result.append((name, state))

    return result


def get_paths_reading(pool: EntropyPool, count: int) -> List[Tuple[str, str]]:
    """Select Paths and assign states. One byte per state, no transforms."""
    if count == 0:
        return []

    safe_count = min(count, len(paths))
    chosen = pool.draw_sample(paths, safe_count)

    result = []
    for path_name in chosen:
        state = pool.draw_state()
        result.append((path_name, state))

    return result


# === VEIL HANDLERS ===

def handle_veil_reading(world_key: str, world_info: dict, pool: EntropyPool):
    """Special output for the Three Veils of Negative Existence."""
    if world_key == "Ain":
        console.print("\n[bold white on black]  ∅  THE VOID  ∅  [/bold white on black]")
        console.print("[dim]Your question returns to silence. There is nothing to read.[/dim]")
        console.print("[dim]This is not an error — it is the answer.[/dim]\n")

    elif world_key == "Ain Sof":
        console.print("\n[bold white]  ∞  THE LIMITLESS  ∞  [/bold white]")
        console.print("[dim]The situation is unbounded. No fixed outcome exists.[/dim]")
        console.print("[dim]All paths remain equally open.[/dim]\n")

    elif world_key == "Ain Sof Aur":
        console.print("\n[bold yellow]  ✦  LIMITLESS LIGHT  ✦  [/bold yellow]")
        console.print("[dim]Potential coalesces but has not taken form.[/dim]")
        # One whisper from the edge of manifestation
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
              "0: Automatic (1-10 Sephiroth)\n"
              "1: Single Sephirah\n"
              "3: Three Pillars (default)\n"
              "10: Full Tree of Life\n"
              "4: Four Worlds Reading")
    )
    parser.add_argument(
        '-p', '--paths', type=int,
        help=f"Number of paths (0-{NUM_PATHS}). Default: random."
    )
    args = parser.parse_args()

    question = args.query
    reading_type = args.reading_type

    # Fetch entropy
    raw_pool = get_random_org_pool(256)
    pool = EntropyPool(raw_pool)

    # Auth hash from first 32 bytes consumed
    auth_bytes = bytes([pool.draw() for _ in range(32)])
    auth_string = hashlib.sha256(auth_bytes).hexdigest()[:8].upper()

    # Select World (weighted)
    world_keys = list(SEVEN_WORLDS.keys())
    world_weights = [SEVEN_WORLDS[k]["weight"] for k in world_keys]
    selected_world_key = pool.draw_weighted(world_keys, world_weights)
    selected_world = SEVEN_WORLDS[selected_world_key]

    # Display header
    console.print(f"\n[bold purple]Kabbalistic Divination for:[/bold purple] '{question}'")
    console.print(f"[dim]Entropy Source: Random.org (True Atmospheric Noise)[/dim]",
                  highlight=False)
    console.print(f"[dim]Auth:[/dim] [bold green]{auth_string}[/bold green]")
    console.print(f"[bold cyan]World:[/bold cyan] {selected_world['name']}")
    console.print(f"[dim]{selected_world['description']}[/dim]")

    # If a Veil was drawn, handle specially and exit
    if selected_world_key in VEILS:
        handle_veil_reading(selected_world_key, selected_world, pool)
        #console.print(f"[dim]Entropy consumed: {pool.consumed} bytes[/dim]")
        return

    # Determine Sephirot count
    if reading_type in ('4', '10'):
        sephirot_count = 10
    elif reading_type == '0':
        sephirot_count = pool.draw_uniform(10) + 1  # [1, 10]
    else:
        sephirot_count = int(reading_type)

    revealed_sephirot = get_sephirot_reading(pool, sephirot_count)

    # Determine path count
    if args.paths is not None:
        path_count = args.paths
        if not (0 <= path_count <= NUM_PATHS):
            console.print(f"[red]Error: Path count must be 0-{NUM_PATHS}.[/red]")
            return
    else:
        path_count = pool.draw_uniform(NUM_PATHS + 1)  # [0, 22]

    revealed_paths = get_paths_reading(pool, path_count)

    # Display Sephiroth
    console.print("\n[bold magenta]The Revealed Sephiroth:[/bold magenta]")

    if reading_type == '4':
        world_readings = {wn: [] for wn in worlds_grouping}
        for sephirah, state in revealed_sephirot:
            for world_name, sephirot_in_world in worlds_grouping.items():
                if sephirah in sephirot_in_world:
                    world_readings[world_name].append(
                        f"{sephirah} {format_state(state)}")
        for world_name, readings in world_readings.items():
            if readings:
                console.print(f"  [bold]{world_name} World:[/bold] {', '.join(readings)}")
    else:
        for i, (name, state) in enumerate(revealed_sephirot):
            console.print(f"  [bold]{i+1}. {name}[/bold] {format_state(state)}")

    # Display Paths
    if revealed_paths:
        console.print(f"\n[bold magenta]The Revealed Paths:[/bold magenta]")
        for i, (name, state) in enumerate(revealed_paths):
            console.print(f"  [bold]{i+1}. {name}[/bold] {format_state(state)}")

    #console.print(f"\n[dim]Entropy consumed: {pool.consumed} bytes[/dim]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]⏹️ Revelation canceled.[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred: {e}[/bold red]")
