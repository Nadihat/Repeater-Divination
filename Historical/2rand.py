#!/usr/bin/env python3
"""
entropy_oracle.py
Pulls 100% true random words from a set of 100 using Random.org atmospheric noise.
"""

import sys
import argparse
import urllib.request
import hashlib
from typing import List
from rich.console import Console
from rich.table import Table

console = Console()

# === THE 100 WORD LIST ===
WORDS = [
    "Abundance", "Action", "Anchor", "Balance", "Beacon", "Belief", "Bloom", "Brave", "Bridge", "Bright",
    "Calm", "Chance", "Change", "Clarity", "Compass", "Courage", "Create", "Crystal", "Dance", "Daring",
    "Dawn", "Depth", "Desert", "Dream", "Earth", "Echo", "Element", "Energy", "Enigma", "Essence",
    "Eternal", "Fable", "Flame", "Flight", "Flow", "Forest", "Fortune", "Freedom", "Future", "Garden",
    "Ghost", "Glory", "Grace", "Gravity", "Growth", "Harmony", "Heart", "Hidden", "Honest", "Horizon",
    "Humble", "Icon", "Impact", "Infinity", "Insight", "Island", "Journey", "Justice", "Kindle", "Kingdom",
    "Legacy", "Legend", "Light", "Logic", "Loyal", "Magic", "Memory", "Mirror", "Moment", "Motion",
    "Nature", "Nebula", "Night", "Noble", "Ocean", "Oracle", "Origin", "Passage", "Patience", "Peace",
    "Phantom", "Phoenix", "Pillar", "Portal", "Power", "Prism", "Pure", "Quiet", "Radiant", "Reason",
    "Relic", "Rhythm", "River", "Sacred", "Shadow", "Silence", "Silver", "Spirit", "Storm", "Summer",
    "Temple", "Theory", "Thunder", "Time", "Trace", "Truth", "Unity", "Valley", "Vessel", "Vision",
    "Voice", "Wander", "Water", "Whisper", "Wild", "Will", "Wind", "Winter", "Wisdom", "Zenith"
]

def fetch_true_random_indices(n: int) -> List[int]:
    """Connects to Random.org to get true random indices (0-99)."""
    # Fetch slightly more than needed to account for potential duplicates
    fetch_count = n + 10 if n < 90 else 100
    url = f"https://www.random.org/integers/?num={fetch_count}&min=0&max=99&col=1&base=10&format=plain&rnd=new"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'EntropyOracle/1.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            data = response.read().decode('utf-8').strip()
            if not data or data.startswith("Error"):
                raise ValueError(f"Random.org Error: {data}")
            
            raw_nums = [int(x) for x in data.split('\n') if x.strip()]
            
            # Deduplicate while preserving order
            unique_indices = []
            for num in raw_nums:
                if num not in unique_indices:
                    unique_indices.append(num)
                if len(unique_indices) == n:
                    break
            return unique_indices
    except Exception as e:
        console.print(f"[bold red]API Error:[/bold red] {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="True Entropy Word Puller")
    parser.add_argument('-q', '--query', required=True, help='The question or focal point.')
    parser.add_argument('-n', '--num', type=int, default=3, help='Number of words (1-20).')
    args = parser.parse_args()

    if not 1 <= args.num <= 100:
        console.print("[red]Select between 1 and 100 words.[/red]")
        return

    # 1. Fetch from Random.org
    with console.status("[bold cyan]Fetching atmospheric noise from Random.org..."):
        indices = fetch_true_random_indices(args.num)

    # 2. Generate Auth Signature (for consistency checks)
    query_hash = hashlib.sha256(args.query.encode()).hexdigest().upper()
    session_auth = query_hash[:8]
    entropy_sig = hashlib.md5(str(indices).encode()).hexdigest()[:12].upper()

    # 3. Build Output Table
    console.print(f"\n[bold magenta]ENTROPY ORACLE[/bold magenta]")
    console.print(f"[dim]Query:[/dim] [italic]'{args.query}'[/italic]")
    console.print(f"[dim]Session Auth:[/dim] [green]{session_auth}[/green] | [dim]Entropy Sig:[/dim] [cyan]{entropy_sig}[/cyan]")
    console.print(f"[dim]Source:[/dim] Random.org (True Atmospheric Noise)\n")

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("#", style="dim", width=4)
    table.add_column("Index", style="yellow")
    table.add_column("Revealed Word", style="bold white")

    for i, idx in enumerate(indices, 1):
        table.add_row(str(i), str(idx), WORDS[idx])

    console.print(table)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Session terminated.[/red]")
