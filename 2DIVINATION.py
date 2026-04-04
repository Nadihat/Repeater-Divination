#!/usr/bin/env python3
"""
DIVINATION.py
Multi-system divination tool using blind number selection.
Four traditions, one reading, one hidden shuffle.

The user picks numbers without knowing the mapping.
The mapping is a permutation seeded from the question + timestamp.
Bias is structurally impossible — every outcome is equally likely at every position.

Usage:
    python3 DIVINATION.py
"""

import hashlib
import time
import random
import sys
import argparse
from os import urandom

# ----- Optional color UI via rich -----
try:
    from rich.console import Console
    from rich.table import Table
    console = Console()
    RICH = True
except ImportError:
    RICH = False

# === DATA CONSTANTS ===

# --- TAROT: 78 cards × 2 orientations = 156 states ---
MAJOR_ARCANA = [
    "The Fool", "The Magician", "The High Priestess", "The Empress",
    "The Emperor", "The Hierophant", "The Lovers", "The Chariot",
    "Strength", "The Hermit", "Wheel of Fortune", "Justice",
    "The Hanged Man", "Death", "Temperance", "The Devil",
    "The Tower", "The Star", "The Moon", "The Sun",
    "Judgement", "The World"
]
SUITS = ["Wands", "Cups", "Swords", "Pentacles"]
RANKS = ["Ace"] + [str(n) for n in range(2, 11)] + ["Page", "Knight", "Queen", "King"]

TAROT_CARDS = MAJOR_ARCANA + [f"{rank} of {suit}" for suit in SUITS for rank in RANKS]
TAROT_STATES = [f"{card} ({ori})" for card in TAROT_CARDS for ori in ["Upright", "Reversed"]]
# 156 total states

CELTIC_CROSS_POSITIONS = [
    "The Heart of the Matter", "The Crossing Card (Challenge)", "The Foundation (Basis)",
    "The Recent Past", "The Crown (Potential Outcome)", "The Near Future",
    "Yourself / Your Attitude", "Your Environment / External Influences",
    "Hopes and Fears", "The Final Outcome"
]

# --- I CHING: 64 hexagrams ---
ICHING_HEXAGRAMS = [
    "1. ䷀ Qián (The Creative / Force)",
    "2. ䷁ Kūn (The Receptive / Field)",
    "3. ䷂ Zhūn (Difficulty at the Beginning / Sprouting)",
    "4. ䷃ Méng (Youthful Folly / Enveloping)",
    "5. ䷄ Xū (Waiting / Attending)",
    "6. ䷅ Sòng (Conflict / Arguing)",
    "7. ䷆ Shī (The Army / Leading)",
    "8. ䷇ Bǐ (Holding Together / Grouping)",
    "9. ䷈ Xiǎo Chù (Small Taming / Small Accumulating)",
    "10. ䷉ Lǚ (Treading /履)",
    "11. ䷊ Tài (Peace / Pervading)",
    "12. ䷋ Pǐ (Standstill / Obstruction)",
    "13. ䷌ Tóng Rén (Fellowship / Concording People)",
    "14. ䷍ Dà Yǒu (Great Possession / Great Harvesting)",
    "15. ䷎ Qiān (Modesty / Humbling)",
    "16. ䷏ Yù (Enthusiasm / Providing-For)",
    "17. ䷐ Suí (Following / 随)",
    "18. ䷑ Gǔ (Work on the Decayed / Correcting)",
    "19. ䷒ Lín (Approach / Nearing)",
    "20. ䷓ Guān (Contemplation / Viewing)",
    "21. ䷔ Shì Kè (Biting Through / Gnawing Bite)",
    "22. ䷕ Bì (Grace / Adorning)",
    "23. ䷖ Bō (Splitting Apart / Stripping)",
    "24. ䷗ Fù (Return / Turning Back)",
    "25. ䷘ Wú Wàng (Innocence / Without Embroiling)",
    "26. ䷙ Dà Chù (Great Taming / Great Accumulating)",
    "27. ䷚ Yí (Nourishment / Swallowing)",
    "28. ䷛ Dà Guò (Great Exceeding / Great Surpassing)",
    "29. ䷜ Kǎn (The Abysmal / Gorge)",
    "30. ䷝ Lí (The Clinging / Radiance)",
    "31. ䷞ Xián (Influence / Conjoining)",
    "32. ䷟ Héng (Duration / Persevering)",
    "33. ䷠ Dùn (Retreat / Retiring)",
    "34. ䷡ Dà Zhuàng (Great Power / Great Invigorating)",
    "35. ䷢ Jìn (Progress / Prospering)",
    "36. ䷣ Míng Yí (Darkening of the Light / Brilliance Injured)",
    "37. ䷤ Jiā Rén (The Family / Dwelling People)",
    "38. ䷥ Kuí (Opposition / Polarizing)",
    "39. ䷦ Jiǎn (Obstruction / Limping)",
    "40. ䷧ Xiè (Deliverance / Taking-Apart)",
    "41. ䷨ Sǔn (Decrease / Diminishing)",
    "42. ䷩ Yì (Increase / Augmenting)",
    "43. ䷪ Guài (Breakthrough / Displacement)",
    "44. ䷫ Gòu (Coming to Meet / Coupling)",
    "45. ䷬ Cuì (Gathering Together / Clustering)",
    "46. ䷭ Shēng (Pushing Upward / Ascending)",
    "47. ䷮ Kùn (Oppression / Confining)",
    "48. ䷯ Jǐng (The Well / Welling)",
    "49. ䷰ Gé (Revolution / Skinning)",
    "50. ䷱ Dǐng (The Cauldron / Holding)",
    "51. ䷲ Zhèn (The Arousing / Shake)",
    "52. ䷳ Gèn (Keeping Still / Bound)",
    "53. ䷴ Jiàn (Development / Infiltrating)",
    "54. ䷵ Guī Mèi (The Marrying Maiden / Converting)",
    "55. ䷶ Fēng (Abundance / Abounding)",
    "56. ䷷ Lǚ (The Wanderer / Sojourning)",
    "57. ䷸ Xùn (The Gentle / Ground)",
    "58. ䷹ Duì (The Joyous / Open)",
    "59. ䷺ Huàn (Dispersion / Dispersing)",
    "60. ䷻ Jié (Limitation / Articulating)",
    "61. ䷼ Zhōng Fú (Inner Truth / Center Returning)",
    "62. ䷽ Xiǎo Guò (Small Exceeding / Small Surpassing)",
    "63. ䷾ Jì Jì (After Completion / Already Fording)",
    "64. ䷿ Wèi Jì (Before Completion / Not-Yet Fording)"
]

# --- KABBALAH: 10 Sephiroth × 3 states + 22 Paths + Da'at = 35 states ---
SEPHIROT = [
    "Keter (Crown)", "Chokmah (Wisdom)", "Binah (Understanding)",
    "Chesed (Mercy)", "Gevurah (Strength)", "Tiferet (Beauty)",
    "Netzach (Victory)", "Hod (Splendor)", "Yesod (Foundation)",
    "Malkuth (Kingdom)"
]

KABBALAH_PATHS = [
    "Path of Aleph (Air)", "Path of Beth (Mercury)", "Path of Gimel (Moon)",
    "Path of Daleth (Venus)", "Path of Heh (Aries)", "Path of Vav (Taurus)",
    "Path of Zayin (Gemini)", "Path of Cheth (Cancer)", "Path of Teth (Leo)",
    "Path of Yod (Virgo)", "Path of Kaph (Jupiter)", "Path of Lamed (Libra)",
    "Path of Mem (Water)", "Path of Nun (Scorpio)", "Path of Samekh (Sagittarius)",
    "Path of Ayin (Capricorn)", "Path of Peh (Mars)", "Path of Tzaddi (Aquarius)",
    "Path of Qoph (Pisces)", "Path of Resh (Sun)", "Path of Shin (Fire)",
    "Path of Tav (Saturn)"
]

KABBALAH_STATES = (
    # 10 Sephiroth × 3 states = 30
    [f"{s} — Balanced" for s in SEPHIROT]
    + [f"{s} — Excessive" for s in SEPHIROT]
    + [f"{s} — Deficient" for s in SEPHIROT]
    # Da'at: 2 states (never Balanced — it's the Abyss)
    + ["Da'at (Knowledge) — Excessive ⚡ The Abyss is Bridged",
       "Da'at (Knowledge) — Deficient 🌑 The Abyss is Silent"]
    # 22 Paths × 3 states = 66
    + [f"{p} — Flowing" for p in KABBALAH_PATHS]
    + [f"{p} — Excessive" for p in KABBALAH_PATHS]
    + [f"{p} — Deficient" for p in KABBALAH_PATHS]
)
# Total: 30 + 2 + 66 = 98 states
KABBALAH_SIZE = len(KABBALAH_STATES)  # 98

# --- RUNES: Elder Futhark ---
# 24 runes with orientations + Wyrd (blank, no reversal)
# 9 non-reversible runes (symmetrical) + 15 reversible × 2 + Wyrd = 40 states

REVERSIBLE_RUNES = [
    "ᚠ Fehu (Wealth/Cattle)",
    "ᚢ Uruz (Aurochs/Strength)",
    "ᚦ Thurisaz (Giant/Thorn)",
    "ᚨ Ansuz (God/Mouth/Odin)",
    "ᚱ Raidho (Ride/Journey)",
    "ᚲ Kenaz (Torch/Knowledge)",
    "ᚹ Wunjo (Joy/Bliss)",
    "ᚺ Hagalaz (Hail/Disruption)",
    "ᚾ Naudhiz (Need/Constraint)",
    "ᛈ Perthro (Lot Cup/Mystery)",
    "ᛉ Algiz (Elk/Protection)",
    "ᛊ Sowilo (Sun/Victory)",
    "ᛏ Tiwaz (Tyr/Justice)",
    "ᛒ Berkano (Birch/Birth)",
    "ᛚ Laguz (Water/Lake)"
]

NON_REVERSIBLE_RUNES = [
    "ᛁ Isa (Ice/Stillness)",
    "ᛃ Jera (Year/Harvest)",
    "ᛇ Eihwaz (Yew/Endurance)",
    "ᛖ Ehwaz (Horse/Partnership)",
    "ᛗ Mannaz (Man/Humanity)",
    "ᛜ Ingwaz (Ing/Fertility)",
    "ᛞ Dagaz (Day/Dawn)",
    "ᛟ Othala (Heritage/Ancestral Home)",
    "ᚷ Gebo (Gift/Exchange)"
]

RUNE_STATES = (
    [f"{r} — Upright" for r in REVERSIBLE_RUNES]
    + [f"{r} — Merkstave (Reversed)" for r in REVERSIBLE_RUNES]
    + NON_REVERSIBLE_RUNES  # These appear only once (no orientation)
    + ["⬜ Wyrd (Blank Rune — Fate/The Unknowable)"]
)
# Total: 15×2 + 9 + 1 = 40 states
RUNE_SIZE = len(RUNE_STATES)  # 40

RUNE_SPREAD_POSITIONS = {
    1: ["The Situation"],
    3: ["Past / Root Cause", "Present / Challenge", "Future / Outcome"],
    5: ["Past", "Present", "Future", "Advice", "Outcome"]
}


# === THE MAPPER ===

class DivinationMapper:
    """Creates a unique hidden permutation of all divination systems from a seed."""

    def __init__(self, seed: bytes):
        self.rng = random.Random(int.from_bytes(seed, 'big'))

        # Shuffle each system independently
        tarot = TAROT_STATES.copy()
        self.rng.shuffle(tarot)
        self.tarot_map = tarot

        iching = ICHING_HEXAGRAMS.copy()
        self.rng.shuffle(iching)
        self.iching_map = iching

        kabbalah = KABBALAH_STATES.copy()
        self.rng.shuffle(kabbalah)
        self.kabbalah_map = kabbalah

        runes = RUNE_STATES.copy()
        self.rng.shuffle(runes)
        self.runes_map = runes

    def map_one(self, number: int, system_map: list) -> str:
        return system_map[number - 1]

    def map_list(self, numbers: list, system_map: list) -> list:
        return [self.map_one(n, system_map) for n in numbers]


# === INPUT VALIDATION ===

def get_valid_number(prompt: str, min_val: int, max_val: int) -> int:
    while True:
        try:
            number = int(input(prompt))
            if min_val <= number <= max_val:
                return number
            print(f"  Error: Number must be between {min_val} and {max_val}.")
        except ValueError:
            print("  Error: Please enter a valid whole number.")

def get_valid_list(prompt: str, min_val: int, max_val: int,
                   allowed_counts: list = None, allow_empty: bool = False) -> list:
    while True:
        user_input = input(prompt).strip()
        if not user_input and allow_empty:
            return []
        if not user_input and allowed_counts:
            print(f"  Error: Please provide {' or '.join(map(str, allowed_counts))} numbers.")
            continue

        parts = [p.strip() for p in user_input.split(',') if p.strip()]

        if allowed_counts and len(parts) not in allowed_counts:
            print(f"  Error: Please provide exactly {' or '.join(map(str, allowed_counts))} numbers.")
            continue

        numbers, seen, ok = [], set(), True
        try:
            for part in parts:
                num = int(part)
                if not (min_val <= num <= max_val):
                    print(f"  Error: {num} is out of range ({min_val}-{max_val}).")
                    ok = False
                    break
                if num in seen:
                    print(f"  Error: {num} is duplicated. Each number must be unique.")
                    ok = False
                    break
                seen.add(num)
                numbers.append(num)
            if ok:
                return numbers
        except ValueError:
            print(f"  Error: '{part}' is not a valid number.")


# === DISPLAY ===

def format_section(title: str, lines: list) -> str:
    """Format a section of the summary."""
    section = f"\n--- {title} ---\n"
    for line in lines:
        section += line + "\n"
    return section

def print_summary(question: str, auth: str, data: dict):
    """Prints the final summary for interpretation."""
    border = "=" * 60
    print(f"\n{border}")
    print(" DIVINATION QUERY SUMMARY ".center(60, "="))
    print(border)

    summary = f'My Question: "{question}"\nAuth: {auth}\n'
    summary += "\nPlease interpret the following multi-system divination reading.\n"
    summary += "Each system was independently shuffled using entropy.\n"

    # --- Tarot ---
    tarot_numbers = data['user_tarot']
    tarot_results = data['result_tarot']
    lines = []
    if len(tarot_results) == 1:
        lines.append(f"Single Draw: {tarot_results[0]} (position {tarot_numbers[0]} of 156)")
    elif len(tarot_results) == 3:
        labels = ["Past", "Present", "Future"]
        for i, label in enumerate(labels):
            lines.append(f"{i+1}. {label}: {tarot_results[i]} (position {tarot_numbers[i]})")
    elif len(tarot_results) == 10:
        for i, pos in enumerate(CELTIC_CROSS_POSITIONS):
            lines.append(f"{i+1}. {pos}: {tarot_results[i]} (position {tarot_numbers[i]})")
    summary += format_section("Tarot", lines)

    # --- I Ching ---
    lines = [
        f"Hexagram: {data['result_iching']} (position {data['user_iching']} of 64)"
    ]
    if data['iching_lines']:
        lines.append(f"Moving Lines: {', '.join(map(str, data['iching_lines']))}")
    else:
        lines.append("Moving Lines: None (stable hexagram)")
    summary += format_section("I Ching", lines)

    # --- Kabbalah ---
    lines = []
    if data['user_kabbalah']:
        for orig, mapped in zip(data['user_kabbalah'], data['result_kabbalah']):
            lines.append(f"Position {orig}: {mapped}")
    else:
        lines.append("(Skipped)")
    summary += format_section(f"Kabbalah (from {KABBALAH_SIZE} possible states)", lines)

    # --- Runes ---
    lines = []
    if data['user_runes']:
        rune_results = data['result_runes']
        positions = RUNE_SPREAD_POSITIONS.get(len(rune_results))
        if positions:
            for i, (pos, result) in enumerate(zip(positions, rune_results)):
                lines.append(f"{i+1}. {pos}: {result}")
        else:
            for i, (orig, mapped) in enumerate(zip(data['user_runes'], rune_results)):
                lines.append(f"Position {orig}: {mapped}")
    else:
        lines.append("(Skipped)")
    summary += format_section(f"Runes (from {RUNE_SIZE} possible states)", lines)

    print(summary.strip())
    print("-" * 60)


# === MAIN ===

def main():
    parser = argparse.ArgumentParser(
        description="Multi-system divination via blind number selection.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-q', '--query', type=str, default=None,
                        help='Your question (or omit for interactive prompt).')
    args = parser.parse_args()

    print("=" * 60)
    print(" MULTI-SYSTEM DIVINATION ".center(60, "="))
    print("=" * 60)
    print("You pick numbers without knowing the mapping.")
    print("The shuffle is unique to your question and this moment.\n")

    if args.query:
        question = args.query
        print(f'Question: "{question}"')
    else:
        question = input("Inscribe your question: ").strip()
        if not question:
            print("No question provided. Exiting.")
            return

    # --- Seed Generation ---
    # 32 bytes of OS entropy — the shuffle is truly random
    entropy = urandom(32)
    # Mix in the question so different questions diverge even with same entropy
    seed_material = entropy + question.encode('utf-8')
    seed = hashlib.sha256(seed_material).digest()
    auth_string = hashlib.sha256(entropy).hexdigest()[:8].upper()

    print(f"\nInitializing unique session...")
    print(f"Auth: {auth_string}")

    mapper = DivinationMapper(seed)

    print("Session locked. The hidden mapping is now fixed.\n")
    print("-" * 60)

    # === GATHER INPUT ===
    data = {}

    # --- Tarot ---
    print(f"\n TAROT — Pick 1, 3, or 10 numbers from 1 to {len(TAROT_STATES)}")
    print("  (1 = Single Draw, 3 = Past/Present/Future, 10 = Celtic Cross)")
    data['user_tarot'] = get_valid_list(
        "Your numbers: ", 1, len(TAROT_STATES), allowed_counts=[1, 3, 10]
    )

    # --- I Ching ---
    print(f"\n I CHING — Pick a number from 1 to {len(ICHING_HEXAGRAMS)}")
    data['user_iching'] = get_valid_number("Your number: ", 1, len(ICHING_HEXAGRAMS))

    print("Moving lines (1-6, comma-separated, or Enter for none):")
    data['iching_lines'] = get_valid_list("Lines: ", 1, 6, allow_empty=True)

    # --- Kabbalah ---
    print(f"\n KABBALAH — Pick 1 to 10 numbers from 1 to {KABBALAH_SIZE}")
    print(f"  ({KABBALAH_SIZE} states: 10 Sephiroth × 3 conditions + Da'at + 22 Paths × 3 conditions)")
    print("  (Or press Enter to skip)")
    data['user_kabbalah'] = get_valid_list(
        "Your numbers: ", 1, KABBALAH_SIZE, allow_empty=True
    )

    # --- Runes ---
    print(f"\n RUNES — Pick 1, 3, or 5 numbers from 1 to {RUNE_SIZE}")
    print(f"  ({RUNE_SIZE} states: 15 reversible × 2 + 9 non-reversible + Wyrd)")
    print("  (1 = Single, 3 = Past/Present/Future, 5 = Extended)")
    data['user_runes'] = get_valid_list(
        "Your numbers: ", 1, RUNE_SIZE, allowed_counts=[1, 3, 5]
    )

    # === MAP RESULTS ===
    data['result_tarot'] = mapper.map_list(data['user_tarot'], mapper.tarot_map)
    data['result_iching'] = mapper.map_one(data['user_iching'], mapper.iching_map)
    data['result_kabbalah'] = mapper.map_list(data['user_kabbalah'], mapper.kabbalah_map)
    data['result_runes'] = mapper.map_list(data['user_runes'], mapper.runes_map)

    # === DISPLAY ===
    print_summary(question, auth_string, data)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Divination canceled.")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
