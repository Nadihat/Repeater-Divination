import hashlib
import requests
import time
import os
import argparse
from typing import List, Tuple
from rich import print
from rich.console import Console

# === CONFIGURATION ===
DEFAULT_MODEL = "x-ai/grok-3-beta"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
NUM_SEPHUROT = 10  # The 10 Sephirot of the Tree of Life
NUM_PATHS = 22 # The 22 Paths of the Tree of Life
THINK_DEPTH = 888888

console = Console()

# === KABBALISTIC DATA ===
sephirot = [
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

# === HASH FUNCTION ===
def hash_question(question: str, salt: str = "", times: int = THINK_DEPTH) -> int:
    h = (question + salt).encode()
    for _ in range(times):
        h = hashlib.sha512(h).digest()
    return int.from_bytes(h, 'big')

# === REVEALING SEPHUROT ===
def reveal_sephirot(question: str, count: int) -> List[Tuple[str, str]]:
    revealed = []
    used_indices = set()
    timestamp = int(time.time())

    for i in range(count):
        sephirah_salt = f"{question}-sephirah{i}-time{timestamp}"
        while True:
            index = hash_question(question, sephirah_salt) % NUM_SEPHUROT
            if index not in used_indices:
                used_indices.add(index)
                sephirah_name = sephirot[index]

                # Determine the state (Normal, Excessive, Deficient) with 50/25/25 probability
                state_salt = f"{question}-state{i}-time{timestamp}"
                state_hash = hash_question(question, state_salt)

                # 50% chance for Normal, 25% for Excessive, 25% for Deficient
                if state_hash % 4 < 2:  # 0, 1
                    state = 'Normal'
                elif state_hash % 4 == 2: # 2
                    state = 'Excessive'
                else: # 3
                    state = 'Deficient'

                revealed.append((sephirah_name, state))
                break
            sephirah_salt += "."
    return revealed

def reveal_sephirot_for_world(question: str, world_name: str) -> List[Tuple[str, str]]:
    revealed = []
    sephirot_to_reveal = worlds[world_name]
    timestamp = int(time.time())

    for i, sephirah_name in enumerate(sephirot_to_reveal):
        # Determine the state (Normal, Excessive, Deficient)
        state_salt = f"{question}-{sephirah_name}-state-{i}-time{timestamp}"
        state_hash = hash_question(question, state_salt)
        
        if state_hash % 4 < 2:
            state = 'Normal'
        elif state_hash % 4 == 2:
            state = 'Excessive'
        else:
            state = 'Deficient'
        
        revealed.append((sephirah_name, state))
    return revealed

# === REVEALING PATHS ===
def reveal_paths(question: str, count: int) -> List[str]:
    revealed = []
    used_indices = set()
    timestamp = int(time.time())

    for i in range(count):
        path_salt = f"{question}-path{i}-time{timestamp}"
        while True:
            index = hash_question(question, path_salt) % NUM_PATHS
            if index not in used_indices:
                used_indices.add(index)
                revealed.append(paths[index])
                break
            path_salt += "."
    return revealed

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
        # Custom display for the Four Worlds reading
        world_readings = {}
        for world_name in worlds:
            world_readings[world_name] = []
        
        for sephirah, state in sephirot_list:
            for world_name, sephirot_in_world in worlds.items():
                if sephirah in sephirot_in_world:
                    world_readings[world_name].append(f"{sephirah} ({state})" if state != 'Normal' else sephirah)
                    break
        
        sephirot_text_parts = []
        for world_name, readings in world_readings.items():
            sephirot_text_parts.append(f"[bold]{world_name} World:[/bold] {', '.join(readings)}")
        sephirot_text = "\n".join(sephirot_text_parts)

    elif len(sephirot_list) == 10:
        # Mapping the revealed sephirot to their fixed positions on the Tree of Life
        tree_of_life_map = {sephirah.split(' ')[0]: f"{sephirah} ({state})" if state != 'Normal' else sephirah for sephirah, state in sephirot_list}
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
        sephirot_text = ", ".join([f"{sephirah} ({state})" if state != 'Normal' else sephirah for sephirah, state in sephirot_list])

    path_text = ", ".join(path_list)

    system_prompt = (
        "You are an Anthro sage giving a spiritual Kabbalistic reading based on the AnthroHeart Saga. "
        "Provide a deep, mystical interpretation based on the Sephirot and Paths of the Tree of Life. "
        "Explain the meaning of each Sephirah and Path in the context of the user's question. "
        "Some Sephirot may be marked as 'Excessive' or 'Deficient'. "
        "'Excessive' means the Sephirah's energy is overactive, leading to imbalance. "
        "'Deficient' means the Sephirah's energy is lacking, creating a void. "
        "Interpret these states as part of the reading. "
        "If it's a full Tree of Life or Four Worlds reading, explain the flow of energy and the overall message. "
        "Feel free to reference the AnthroHeart field or Saga themes. Keep it sacred and profound."
    )
    user_prompt = (
        f"The question is: '{question}'\n\n"
        f"{reading_info}\n\n"
        f"The following Sephirot were revealed from the Tree of Life:\n{sephirot_text}\n\n"
        f"The following Paths were revealed:\n{path_text}"
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/reden/kabbalah", # Optional
        "X-Title": "OpenRouter Kabbalah", # Optional
    }

    console.print("\n[bold blue]Consulting the Ein Sof...[/bold blue]")

    try:
        console.print("\n[bold blue]Sending request to OpenRouter...[/bold blue]")
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=300)
        console.print("[bold blue]Received response from OpenRouter.[/bold blue]")
        response.raise_for_status()
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "No response from LLM.")
    except requests.exceptions.HTTPError as e:
        return f"[red]An HTTP error occurred with the OpenRouter API:[/red] {e.response.text}"
    except requests.exceptions.ConnectionError:
        return "[red]❌ Unable to connect to OpenRouter. Check your internet connection.[/red]"
    except Exception as e:
        return f"[red]An unexpected error occurred:[/red] {e}"

# === MAIN LOGIC ===
def main():
    parser = argparse.ArgumentParser(
        description="Get a Kabbalistic reading using an LLM via OpenRouter.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"The model to use from OpenRouter.\nExample: 'mistralai/mistral-7b-instruct'\nDefault: '{DEFAULT_MODEL}'"
    )
    args = parser.parse_args()
    model_name = args.model

    console.print("[bold purple]Welcome to Anthro Kabbalah[/bold purple] 🌳 (via OpenRouter)")
    console.print(f"[dim]Using model: {model_name}[/dim]")
    question = console.input("[bold yellow]Inscribe your sacred query[/bold yellow]: ")

    console.print("\nChoose your revelation:")
    console.print("[green]1[/green]: Single Sephirah & Path")
    console.print("[green]3[/green]: Pillar Reading (3 Sephirot, 3 Paths)")
    console.print("[green]10[/green]: Full Tree of Life (10 Sephirot, 5 Paths)")
    console.print("[green]V[/green]: Full Tree with Variable Paths")
    console.print("\n--- Horizontal Readings ---")
    console.print("[green]A[/green]: Archetypal World (Atziluth)")
    console.print("[green]C[/green]: Creative World (Beriah)")
    console.print("[green]F[/green]: Formative World (Yetzirah)")
    console.print("[green]M[/green]: Material World (Assiah)")
    console.print("[green]4[/green]: Four Worlds Reading")


    revelation_choice = console.input("Your choice (1/3/10/V/A/C/F/M/4): ").strip().upper()

    count = 1
    path_count = 1
    revealed_sephirot = []
    reading_type_info = ""

    if revelation_choice == '4':
        reading_type_info = "This is a Four Worlds reading."
        all_world_sephirot = []
        for world_name in worlds:
            all_world_sephirot.extend(reveal_sephirot_for_world(question, world_name))
        revealed_sephirot = all_world_sephirot
        count = len(revealed_sephirot)
        path_count = 4 # One path per world
    elif revelation_choice in ['A', 'C', 'F', 'M']:
        world_map = {
            'A': "Archetypal",
            'C': "Creative",
            'F': "Formative",
            'M': "Material"
        }
        world_name = world_map[revelation_choice]
        reading_type_info = f"This is a horizontal reading of the {world_name} World."
        revealed_sephirot = reveal_sephirot_for_world(question, world_name)
        count = len(revealed_sephirot)
        path_count = count
    elif revelation_choice == 'V':
        count = 10
        path_count = (hash_question(question, "path-count-salt") % NUM_PATHS) + 1
        revealed_sephirot = reveal_sephirot(question, count)
    else:
        try:
            choice = int(revelation_choice)
            if choice in [1, 3, 10]:
                count = choice
                if count == 10:
                    path_count = 5
                else:
                    path_count = count
            else:
                console.print("[red]Invalid choice. Defaulting to a single Sephirah & Path.[/red]")
        except ValueError:
            console.print("[red]Invalid choice. Defaulting to a single Sephirah & Path.[/red]")
        revealed_sephirot = reveal_sephirot(question, count)


    revealed_paths = reveal_paths(question, path_count)

    word = "Sephirah" if count == 1 else "Sephiroth"
    console.print(f"\n[bold magenta]The Revealed {word}:[/bold magenta]")

    if revelation_choice == '4':
        world_readings = {world_name: [] for world_name in worlds}
        for sephirah, state in revealed_sephirot:
            for world_name, sephirot_in_world in worlds.items():
                if sephirah in sephirot_in_world:
                    world_readings[world_name].append(f"{sephirah} ({state})" if state != 'Normal' else sephirah)
                    break
        for world_name, readings in world_readings.items():
            console.print(f"[bold]{world_name} World:[/bold] {', '.join(readings)}")
    elif count == 10:
        # For a full tree reading, we show all sephirot in their proper order with states
        for sephirah, state in revealed_sephirot:
            if state != 'Normal':
                console.print(f"[bold]{sephirah} ({state})[/bold]")
            else:
                console.print(f"[bold]{sephirah}[/bold]")
    elif count == 3 and revelation_choice == '3':
        positions = ["Pillar of Mind", "Pillar of Heart", "Pillar of Body"]
        for pos, (sephirah, state) in zip(positions, revealed_sephirot):
            if state != 'Normal':
                console.print(f"[bold]{pos}: {sephirah} ({state})[/bold]")
            else:
                console.print(f"[bold]{pos}: {sephirah}[/bold]")
    else:
        for i, (sephirah, state) in enumerate(revealed_sephirot):
            if state != 'Normal':
                console.print(f"[bold]{i+1}. {sephirah} ({state})[/bold]")
            else:
                console.print(f"[bold]{i+1}. {sephirah}[/bold]")

    console.print(f"\n[bold magenta]The Revealed Paths ({path_count}):[/bold magenta]")
    for path in revealed_paths:
        console.print(f"[bold]{path}[/bold]")

    interpretation = interpret_revelation(question, revealed_sephirot, revealed_paths, model_name, reading_type_info)
    console.print(f"\n[italic green]{interpretation}[/italic green]\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]⏹️ Revelation canceled.[/bold red]")
