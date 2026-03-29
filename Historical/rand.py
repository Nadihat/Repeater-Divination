#!/usr/bin/env python3
"""
random_words_true.py
Pulls words from a list of 100 using 100% True Random.org entropy.
"""

import sys
import argparse
import urllib.request
import hashlib
from typing import List
from rich.console import Console

console = Console()

# === DATA: 100 ENGLISH WORDS ===
WORD_LIST = [
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

def get_random_indices(count: int) -> List[int]:
    """
    Fetches true random integers from Random.org.
    The 'min' and 'max' are set to 0-99 to correspond to our list indices.
    """
    # Conserving the Random.org link structure
    # We fetch a few extra to ensure uniqueness if duplicates occur
    num_to_fetch = count + 10 
    url = f"https://www.random.org/integers/?num={num_to_fetch}&min=0&max=99&col=1&base=10&format=plain&rnd=new"
    
    headers = {'User-Agent': 'TrueRandomWordGenerator/1.0'}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        response = urllib.request.urlopen(req)
        data = response.read().decode('utf-8').strip()

        if data.startswith("Error:"):
            print(f"Random.org Error: {data}", file=sys.stderr)
            sys.exit(1)

        # Parse the plain text numbers into a list
        raw_indices = [int(x) for x in data.split('\n') if x.strip()]
        
        # Ensure uniqueness while maintaining order
        unique_indices = []
        for i in raw_indices:
            if i not in unique_indices:
                unique_indices.append(i)
            if len(unique_indices) == count:
                break
                
        return unique_indices

    except Exception as e:
        print(f"Network error fetching from Random.org: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Pull words using 100% Random.org entropy.")
    parser.add_argument('-q', '--query', required=True, help='Your query or focus.')
    parser.add_argument('-n', '--num', type=int, default=5, help='Number of words to pull (1-100).')
    args = parser.parse_args()

    if not (1 <= args.num <= 100):
        console.print("[red]Please choose a number between 1 and 100.[/red]")
        return

    # Fetch unique indices from 0-99 via Random.org
    indices = get_random_indices(args.num)

    # Generate a simple hash of the query for "Auth" display (purely aesthetic)
    auth_hash = hashlib.sha256(args.query.encode()).hexdigest()[:8].upper()

    # Display Results
    console.print(f"\n[bold purple]True Entropy Word Pull for:[/bold purple] '{args.query}'")
    console.print(f"[dim]Entropy Source:[/dim] [link=https://www.random.org]Random.org[/link] (Atmospheric Noise)")
    console.print(f"[dim]Session Auth:[/dim] [bold green]{auth_hash}[/bold green]\n")

    console.print("[bold cyan]The Resulting Words:[/bold cyan]")
    for i, idx in enumerate(indices):
        word = WORD_LIST[idx]
        console.print(f"[bold]{i+1}. {word}[/bold] [dim](Index {idx})[/dim]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Process stopped.[/red]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
