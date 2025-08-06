import hashlib
import time
import os
import argparse
from typing import List, Tuple

# === CONFIGURATION ===
THINK_DEPTH = 888888
TEXT_FILE = "CioSaga.txt"

# === HASH FUNCTION ===
def hash_question(question: str, salt: str = "", times: int = THINK_DEPTH) -> int:
    h = (question + salt).encode()
    for _ in range(times):
        h = hashlib.sha512(h).digest()
    return int.from_bytes(h, 'big')

# === SENTENCE REVEALING ===
def reveal_sentences(question: str, count: int, sentences: List[str]) -> List[str]:
    revealed = []
    used_indices = set()
    timestamp = int(time.time())
    num_sentences = len(sentences)

    if num_sentences == 0:
        return ["The CioSaga text is empty. Please provide the text."]

    for i in range(count):
        sentence_salt = f"{question}-sentence{i}-time{timestamp}"
        while True:
            index = hash_question(question, sentence_salt) % num_sentences
            if index not in used_indices:
                used_indices.add(index)
                revealed.append(sentences[index])
                break
            sentence_salt += "."
    return revealed

# === MAIN LOGIC ===
def main():
    parser = argparse.ArgumentParser(
        description="Get a reading from the CioSaga.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "question",
        type=str,
        help="Your question for the CioSaga."
    )
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        default=3,
        help="Number of sentences to reveal (default: 3)."
    )
    args = parser.parse_args()
    question = args.question
    count = args.number

    try:
        with open(TEXT_FILE, 'r', encoding='utf-8') as f:
            text_content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{TEXT_FILE}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return

    # Parse sentences from the text file
    sentences = [s.strip() for s in text_content.strip().split('.') if s.strip()]

    if not sentences:
        print(f"No sentences found in '{TEXT_FILE}'.")
        return

    print(f"Your question: '{question}'")
    print(f"Revealing {count} sentences from the CioSaga...")

    revealed_sentences = reveal_sentences(question, count, sentences)

    print("\n--- The CioSaga Reveals ---")
    for i, sentence in enumerate(revealed_sentences):
        print(f"{i+1}. {sentence}")
    print("---------------------------\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nRevelation canceled.")