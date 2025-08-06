import hashlib
import requests
import time
import os
import argparse
from typing import List
from rich import print
from rich.console import Console

# === CONFIGURATION ===
# The model can be specified via command-line argument.
# See a list of models at https://openrouter.ai/models
DEFAULT_MODEL = "x-ai/grok-3-beta"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
THINK_DEPTH = 8888888

console = Console()

# === TRADITIONAL CHINESE WORD LIST ===
words = [
    '的', '我', '你', '是', '了', '不', '他', '我們', '在', '有', '她', '們', '這', '那', '個', '人', '家', '學校',
    '朋友', '中國', '台灣', '水', '茶', '食物', '來', '去', '說', '看', '吃', '喝', '做', '想', '要', '會', '喜歡',
    '好', '大', '小', '多', '少', '很', '都', '嗎', '什麼', '誰', '哪裡', '哪兒', '為什麼', '多少', '男人', '女人',
    '孩子', '爸爸', '媽媽', '學生', '老師', '這裡', '那裡', '上面', '下面', '裡面', '外面', '前面', '後面', '商店',
    '香港', '今天', '明天', '昨天', '現在', '早上', '下午', '晚上', '年', '月', '日', '時間', '飯', '菜', '水果',
    '肉', '東西', '錢', '書', '電腦', '手機', '桌子', '椅子', '車', '買', '賣', '寫', '讀', '走', '跑', '坐', '站',
    '開', '關', '給', '拿', '找', '等', '問', '回答', '愛', '知道', '覺得', '希望', '不好', '高', '矮', '長', '短',
    '新', '舊', '老', '漂亮', '帥', '可愛', '好吃', '難吃', '高興', '難過', '累', '忙', '快', '慢', '貴', '便宜',
    '太', '也', '沒', '常常', '最', '就', '才', '本', '張', '杯', '瓶', '碗', '件', '條', '輛', '隻', '呢', '吧',
    '過', '和', '跟', '但是', '因為', '所以', '如果', '還是', '或者', '喂', '啊', '哎呀', '哦'
]
DECK_SIZE = len(words)

# === HASH FUNCTION ===
def hash_question(question: str, salt: str = "", times: int = THINK_DEPTH) -> int:
    h = (question + salt).encode()
    for _ in range(times):
        h = hashlib.sha512(h).digest()
    return int.from_bytes(h, 'big')

# === DRAWING WORDS ===
def draw_words(question: str, count: int) -> List[str]:
    drawn = []
    used_indices = set()
    timestamp = int(time.time())  # Add a bit of time-based randomness

    for i in range(count):
        salt = f"{question}-word{i}-time{timestamp}"
        while True:
            index = hash_question(question, salt) % DECK_SIZE
            if index not in used_indices:
                used_indices.add(index)
                drawn.append(words[index])
                break
    return drawn

# === INTERPRETATION REQUEST ===
def interpret_reading(question: str, word_list: List[str], model: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return (
            "[red]❌ OPENROUTER_API_KEY environment variable not set.[/red]\n"
            "[yellow]💡 Tip: Get a key from https://openrouter.ai and set it.[/yellow]\n"
            "   Linux/macOS: export OPENROUTER_API_KEY='your-key-here'\n"
            "   Windows: setx OPENROUTER_API_KEY your-key-here"
        )

    word_text = ", ".join(word_list)

    system_prompt = (
        "You are a wise sage. Interpret the drawn Traditional Chinese words in a poetic and insightful way, "
        "connecting them to the user's question. Provide a simple, clear, and helpful message."
    )
    user_prompt = (
        f"The question is: '{question}'\n\n"
        f"The following Traditional Chinese word(s) were drawn:\n{word_text}"
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/reden/tcp",
        "X-Title": "Chinese Oracle",
    }


    console.print("\n[bold blue]Consulting the digital ether...[/bold blue]")

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
        description="Get a Traditional Chinese reading using an LLM via OpenRouter.",
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

    console.print("[bold cyan]Traditional Chinese Oracle[/bold cyan] (via OpenRouter)")
    console.print(f"[dim]Using model: {model_name}[/dim]")
    question = console.input("[bold yellow]Ask your question[/bold yellow]: ")

    try:
        word_count = int(console.input("How many words to draw? (1-10): ").strip())
        if not 1 <= word_count <= 10:
            word_count = 3
    except ValueError:
        word_count = 3

    drawn_words = draw_words(question, word_count)

    console.print(f"\n[bold magenta]Your Word{'s' if word_count > 1 else ''}:[/bold magenta]")
    for i, word in enumerate(drawn_words):
        console.print(f"[bold]{i+1}. {word}[/bold]")

    interpretation = interpret_reading(question, drawn_words, model_name)
    console.print(f"\n[italic green]{interpretation}[/italic green]\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]⏹️ Reading canceled.[/bold red]")
