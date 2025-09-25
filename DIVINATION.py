import hashlib
import time
import random

# --- DATA CONSTANTS ---
TAROT_CARDS = [
    "0: The Fool", "1: The Magician", "2: The High Priestess", "3: The Empress",
    "4: The Emperor", "5: The Hierophant", "6: The Lovers", "7: The Chariot",
    "8: Strength", "9: The Hermit", "10: Wheel of Fortune", "11: Justice",
    "12: The Hanged Man", "13: Death", "14: Temperance", "15: The Devil",
    "16: The Tower", "17: The Star", "18: The Moon", "19: The Sun",
    "20: Judgement", "21: The World", "22: Ace of Wands", "23: Two of Wands",
    "24: Three of Wands", "25: Four of Wands", "26: Five of Wands", "27: Six of Wands",
    "28: Seven of Wands", "29: Eight of Wands", "30: Nine of Wands", "31: Ten of Wands",
    "32: Page of Wands", "33: Knight of Wands", "34: Queen of Wands", "35: King of Wands",
    "36: Ace of Cups", "37: Two of Cups", "38: Three of Cups", "39: Four of Cups",
    "40: Five of Cups", "41: Six of Cups", "42: Seven of Cups", "43: Eight of Cups",
    "44: Nine of Cups", "45: Ten of Cups", "46: Page of Cups", "47: Knight of Cups",
    "48: Queen of Cups", "49: King of Cups", "50: Ace of Swords", "51: Two of Swords",
    "52: Three of Swords", "53: Four of Swords", "54: Five of Swords", "55: Six of Swords",
    "56: Seven of Swords", "57: Eight of Swords", "58: Nine of Swords", "59: Ten of Swords",
    "60: Page of Swords", "61: Knight of Swords", "62: Queen of Swords", "63: King of Swords",
    "64: Ace of Pentacles", "65: Two of Pentacles", "66: Three of Pentacles", "67: Four of Pentacles",
    "68: Five of Pentacles", "69: Six of Pentacles", "70: Seven of Pentacles", "71: Eight of Pentacles",
    "72: Nine of Pentacles", "73: Ten of Pentacles", "74: Page of Pentacles", "75: Knight of Pentacles",
    "76: Queen of Pentacles", "77: King of Pentacles"
]
CELTIC_CROSS_POSITIONS = [
    "The Heart of the Matter", "The Crossing Card (Challenge)", "The Foundation (Basis)",
    "The Recent Past", "The Crown (Potential Outcome)", "The Near Future",
    "Yourself / Your Attitude", "Your Environment / External Influences",
    "Hopes and Fears", "The Final Outcome"
]

class DivinationMapper:
    def __init__(self, question):
        combined_salt = (str(time.time()) + question).encode('utf-8')
        current_hash = hashlib.sha256(combined_salt).digest()
        for _ in range(8888):
            current_hash = hashlib.sha256(current_hash).digest()
        self.seed_hash = current_hash.hex()
        self.rng = random.Random(int(self.seed_hash, 16))

        tarot_master = [f"{c} ({ori})" for c in TAROT_CARDS for ori in ["Upright", "Reversed"]]
        self.rng.shuffle(tarot_master)
        self.tarot_map = tarot_master
        ich = list(range(1, 65)); self.rng.shuffle(ich); self.iching_map = ich
        kab = list(range(1, 33)); self.rng.shuffle(kab); self.kabbalah_map = kab
        runes = list(range(1, 26)); self.rng.shuffle(runes); self.runes_map = runes

    def map_number(self, number, system_map):
        return system_map[number - 1]

    def map_list(self, numbers, system_map):
        return [self.map_number(n, system_map) for n in numbers]

# --- HELPER FUNCTIONS FOR INPUT VALIDATION ---

def get_valid_number(prompt, min_val, max_val):
    while True:
        try:
            number = int(input(prompt))
            if min_val <= number <= max_val: return number
            print(f"  Error: Number must be between {min_val} and {max_val}.")
        except ValueError:
            print("  Error: Please enter a valid whole number.")

def get_valid_list(prompt, min_val, max_val, allowed_counts=None):
    while True:
        user_input = input(prompt).strip()
        if not user_input and allowed_counts is None:
            return []
        parts = [p.strip() for p in user_input.split(',') if p.strip()]
        if allowed_counts and len(parts) not in allowed_counts:
            print(f"  Error: Please provide exactly {', '.join(map(str, allowed_counts))} numbers.")
            continue
        numbers, seen, ok = [], set(), True
        try:
            for part in parts:
                num = int(part)
                if not (min_val <= num <= max_val):
                    print(f"  Error: Number ({num}) is out of range {min_val}-{max_val}.")
                    ok = False; break
                if num not in seen:
                    seen.add(num); numbers.append(num)
            if ok: return numbers  # preserve order
        except ValueError:
            print(f"  Error: '{part}' is not a valid number. Please use comma-separated numbers.")

# --- MAIN SCRIPT EXECUTION ---

def print_summary(question, data):
    """Prints the final summary for copy-pasting."""
    print("\n" + "="*50)
    print(" divination query summary ".upper().center(50, "="))
    print("="*50)
    print("You can now copy and paste the text below into your AI assistant.")
    print("-" * 50)
    
    summary = f"""My Question: "{question}"

Please provide an interpretation based on the following divination results.

For this session, all possible outcomes for each system (e.g., all 156 Tarot card states, all 64 I-Ching hexagrams) were arranged in a unique, random order based on my question and the timestamp. The "position" number I provide indicates where in that random sequence the result was drawn from. A lower number means it was drawn from nearer the "top" of the randomized set.

--- Tarot ---
"""
    # Dynamic Tarot Formatting
    user_tarot = data['user_tarot']
    result_tarot = data['result_tarot']
    if len(result_tarot) == 1:
        summary += f"Result: {result_tarot[0]} (drawn from position {user_tarot[0]})\n"
    elif len(result_tarot) == 3:
        summary += "Spread: Past, Present, Future\n"
        labels = ["1. Past", "2. Present", "3. Future"]
        for i, label in enumerate(labels):
            summary += f"{label}: {result_tarot[i]} (drawn from position {user_tarot[i]})\n"
    elif len(result_tarot) == 10:
        summary += "Spread: Celtic Cross\n"
        for i, pos in enumerate(CELTIC_CROSS_POSITIONS):
            summary += f"{i+1}. {pos}: {result_tarot[i]} (drawn from position {user_tarot[i]})\n"

    # I-Ching Formatting
    summary += f"""
--- I-Ching ---
Hexagram: {data['result_iching']} (drawn from position {data['user_iching']})
Moving Lines: {', '.join(map(str, data['iching_lines'])) if data['iching_lines'] else 'None'}
"""
    # Kabbalah Formatting
    summary += f"\n--- Kabbalah ---\n"
    if data['user_kabbalah']:
        kabbalah_pairs = [f"{mapped} (from position {original})" for original, mapped in zip(data['user_kabbalah'], data['result_kabbalah'])]
        summary += f"Numbers: {', '.join(kabbalah_pairs)}\n"
    else: summary += "Numbers: None\n"
        
    # Runes Formatting
    summary += f"\n--- Runes ---\n"
    if data['user_runes']:
        runes_pairs = [f"{mapped} (from position {original})" for original, mapped in zip(data['user_runes'], data['result_runes'])]
        summary += f"Numbers: {', '.join(runes_pairs)}\n"
    else: summary += "Numbers: None\n"

    print(summary.strip())
    print("-" * 50)


def main():
    """Main function to run the divination tool."""
    print("Welcome to the Randomized Divination Query Builder!")
    print("Paste the results into your AI assistant for interpretation.")
    print("First, tell me your question to personalize the session's randomization.")
    
    question = input("Type your question: ")
    
    print("\nInitializing a unique, randomized session based on your question...")
    mapper = DivinationMapper(question)
    
    print("Session initialized. The mapping of numbers to outcomes is now fixed for this unique query.")
    print("-" * 70)
    
    print("\n--- Enter Your Chosen Numbers ---")
    
    data = {}
    data['user_tarot'] = get_valid_list(
        "Tarot (Choose 1, 3, or 10 numbers from 1-156, comma-separated): ", 1, 156, [1, 3, 10]
    )
    data['user_iching'] = get_valid_number("\nI-Ching (Choose a number from 1 to 64): ", 1, 64)
    data['iching_lines'] = get_valid_list("I-Ching Moving Lines (1-6, comma-separated, or Enter for none): ", 1, 6)
    data['user_kabbalah'] = get_valid_list("\nKabbalah (Choose numbers from 1 to 32, comma-separated): ", 1, 32)
    data['user_runes'] = get_valid_list(
    "\nRunes (Choose 1 or 3 numbers from 1 to 25, comma-separated): ",
    1, 25, [1, 3]
    )

    data['result_tarot'] = mapper.map_list(data['user_tarot'], mapper.tarot_map)
    data['result_iching'] = mapper.map_number(data['user_iching'], mapper.iching_map)
    data['result_kabbalah'] = mapper.map_list(data['user_kabbalah'], mapper.kabbalah_map)
    data['result_runes'] = mapper.map_list(data['user_runes'], mapper.runes_map)

    print_summary(question, data)

if __name__ == "__main__":
    main()