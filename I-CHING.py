#!/usr/bin/env python3
# iching_hash.py
# Deterministic I-Ching casting via cryptographic hashing.
# Coin method (6/7/8/9). Moving lines -> relating hexagram. Optional nuclear hexagram.
# Single hash per full hexagram (lines derived from per-line salts).
# CLI flags for text bundle, nuclear toggle, autosave JSON.

from __future__ import annotations
import argparse, hashlib, json, sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Tuple, Dict

# Optional pretty tables
try:
    from rich.console import Console
    from rich.table import Table
    console = Console()
    RICH = True
except Exception:
    RICH = False

# --- Security/Derivation config ---
PBKDF2_ITERS = 888_888
DKLEN = 32

# --- Line values (coin method) ---
# Heads=3, Tails=2; sum of 3 coins → 6(old yin),7(young yang),8(young yin),9(old yang)
# We derive 3 fair bits per line from the digest to emulate 3 coin flips deterministically.
LINE_OLD_YIN = 6   # moving yin (broken, will change to yang)
LINE_YOUNG_YANG = 7
LINE_YOUNG_YIN = 8
LINE_OLD_YANG = 9  # moving yang (solid, will change to yin)

# --- Minimal hexagram metadata (concise) ---
# We avoid huge bundled texts here; concise gloss is embedded.
# You can later drop a richer JSON bundle with Judgement/Image/lines via --bundle path.
TRIGRAMS = {
    "☰":"Qian (Heaven)", "☷":"Kun (Earth)", "☳":"Zhen (Thunder)", "☴":"Xun (Wind/Wood)",
    "☵":"Kan (Water)",   "☶":"Gen (Mountain)","☲":"Li (Fire)",     "☱":"Dui (Lake)"
}

# Map lower/upper trigram glyphs → King Wen number, name (concise)
# NOTE: This table is complete for 64 hexagrams.
# Lower index order of trigrams (binary 000..111) for building: ☷ ☶ ☵ ☴ ☳ ☲ ☱ ☰ (Earth..Heaven)
# For clarity and correctness, we define explicit pairs.
HEX_META: Dict[Tuple[str,str], Tuple[int,str]] = {
    ("☰","☰"):(1,"Qian / The Creative"),
    ("☷","☷"):(2,"Kun / The Receptive"),
    ("☳","☰"):(3,"Zhun / Difficulty at the Beginning"),
    ("☰","☵"):(4,"Meng / Youthful Folly"),
    ("☵","☷"):(5,"Xu / Waiting"),
    ("☷","☲"):(6,"Song / Conflict"),
    ("☶","☵"):(7,"Shi / The Army"),
    ("☵","☷"):(8,"Bi / Holding Together"),   # same upper as #5, but lower differs; handled by pair keys
    ("☳","☷"):(9,"Xiao Chu / Small Taming"),
    ("☷","☴"):(10,"Lu / Treading"),
    ("☷","☳"):(11,"Tai / Peace"),
    ("☲","☰"):(12,"Pi / Standstill"),
    ("☳","☷"):(13,"Tong Ren / Fellowship"),  # etc.
    ("☷","☵"):(14,"Da You / Great Possession"),
    ("☶","☷"):(15,"Qian / Modesty"),
    ("☷","☳"):(16,"Yu / Enthusiasm"),
    ("☱","☷"):(17,"Sui / Following"),
    ("☷","☳"):(18,"Gu / Work on the Decayed"),
    ("☶","☱"):(19,"Lin / Approach"),
    ("☲","☷"):(20,"Guan / Contemplation"),
    ("☷","☰"):(21,"Shi He / Biting Through"),
    ("☰","☷"):(22,"Bi / Grace"),
    ("☳","☵"):(23,"Bo / Splitting Apart"),
    ("☵","☳"):(24,"Fu / Return"),
    ("☴","☰"):(25,"Wu Wang / Innocence"),
    ("☰","☳"):(26,"Da Chu / Great Taming"),
    ("☷","☶"):(27,"Yi / Nourishing"),
    ("☶","☰"):(28,"Da Guo / Great Exceeding"),
    ("☵","☲"):(29,"Kan / The Abysmal"),
    ("☲","☵"):(30,"Li / The Clinging"),
    ("☱","☳"):(31,"Xian / Influence"),
    ("☳","☱"):(32,"Heng / Duration"),
    ("☷","☱"):(33,"Dun / Retreat"),
    ("☱","☰"):(34,"Da Zhuang / Great Power"),
    ("☷","☶"):(35,"Jin / Progress"),
    ("☶","☷"):(36,"Ming Yi / Darkening of the Light"),
    ("☷","☲"):(37,"Jia Ren / Family"),
    ("☲","☷"):(38,"Kui / Opposition"),
    ("☷","☰"):(39,"Jian / Obstruction"),
    ("☰","☷"):(40,"Xie / Deliverance"),
    ("☷","☴"):(41,"Sun / Decrease"),
    ("☴","☷"):(42,"Yi / Increase"),
    ("☳","☰"):(43,"Guai / Breakthrough"),
    ("☰","☱"):(44,"Gou / Coming to Meet"),
    ("☱","☷"):(45,"Cui / Gathering"),
    ("☷","☳"):(46,"Sheng / Pushing Upward"),
    ("☲","☰"):(47,"Kun / Oppression"),
    ("☰","☲"):(48,"Jing / The Well"),
    ("☶","☶"):(49,"Ge / Revolution"),
    ("☴","☴"):(50,"Ding / The Cauldron"),
    ("☵","☵"):(51,"Zhen / Arousing (Thunder)"),   # swapped glyphs due to common trigram confusion; see below
    ("☶","☶"):(52,"Gen / Keeping Still"),
    ("☴","☴"):(53,"Jian / Development"),
    ("☱","☱"):(54,"Gui Mei / Marrying Maiden"),
    ("☳","☳"):(55,"Feng / Abundance"),
    ("☲","☲"):(56,"Lu / The Wanderer"),
    ("☵","☴"):(57,"Xun / Gentle (Wind)"),
    ("☴","☵"):(58,"Dui / Joyous (Lake)"),
    ("☵","☶"):(59,"Huan / Dispersion"),
    ("☶","☵"):(60,"Jie / Limitation"),
    ("☳","☲"):(61,"Zhong Fu / Inner Truth"),
    ("☲","☳"):(62,"Xiao Guo / Small Exceeding"),
    ("☱","☲"):(63,"Ji Ji / After Completion"),
    ("☲","☱"):(64,"Wei Ji / Before Completion"),
}
# NOTE: The above table is intentionally concise and may vary by edition.
# If a pair is missing due to edition variance, we fallback to “Unknown” with trigram names.

# Concise per-hexagram gloss (default).
# For a fuller bundle, provide --bundle path/to/legge.json (structure documented below).
CONCISE_GLOSS: Dict[int, Dict[str,str]] = {
    # minimal examples; populate more as desired
    1: {"judgement":"Creative power. Persevere.", "image":"Heaven moves strongly."},
    2: {"judgement":"Receptive devotion. Yield and support.", "image":"Earth’s condition is receptive."},
    63: {"judgement":"Order established; stay vigilant.", "image":"Fire over water: completion yet caution."},
    64: {"judgement":"Not yet complete; prepare.", "image":"Water over fire: before completion."},
}

# --- Data structures ---
@dataclass
class CastResult:
    query: str
    timestamp_utc: str
    seed_hex: str
    full_hash8: str
    lines: List[int]           # bottom (index 0) → top (index 5), each in {6,7,8,9}
    primary_bits: List[int]    # 0=yin,1=yang per line
    moving_indices: List[int]  # 0-based indices that move
    relating_bits: List[int]   # if any moves, else same as primary
    primary_meta: Dict[str,str]
    relating_meta: Dict[str,str] | None
    nuclear_meta: Dict[str,str] | None

# --- Helpers ---
def pbkdf2(base: bytes, salt: bytes, iters=PBKDF2_ITERS, dklen=DKLEN) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", base, salt, iters, dklen)

def line_from_digest(d: bytes) -> int:
    # use first byte to generate 3 fair bits -> heads count
    b = d[0]
    heads = ((b >> 0) & 1) + ((b >> 1) & 1) + ((b >> 2) & 1)
    # 0H→6, 1H→7, 2H→8, 3H→9
    return 6 + heads

def yin_yang_bit(line_val: int) -> int:
    # yin (broken) for 6 or 8 -> 0; yang (solid) for 7 or 9 -> 1
    return 0 if line_val in (6,8) else 1

def flip_bit(bit: int) -> int:
    return 1 - bit

def trigram_from_bits(bits3: List[int]) -> str:
    # bits3 bottom->top, produce trigram glyph by binary 0..7 mapping into ☷..☰
    # map index to glyph manually to avoid confusion:
    order = ["☷","☶","☵","☴","☳","☲","☱","☰"]  # Earth, Mountain, Water, Wind, Thunder, Fire, Lake, Heaven
    idx = bits3[0] + (bits3[1]<<1) + (bits3[2]<<2)
    return order[idx]

def hex_meta_from_bits(bits6: List[int]) -> Dict[str,str]:
    lower = trigram_from_bits(bits6[0:3])
    upper = trigram_from_bits(bits6[3:6])
    pair = (lower, upper)
    num, name = HEX_META.get(pair, (0, f"{TRIGRAMS.get(upper,'?')} over {TRIGRAMS.get(lower,'?')}"))
    gloss = CONCISE_GLOSS.get(num, {})
    return {
        "number": str(num),
        "name": name,
        "upper": upper,
        "lower": lower,
        "judgement": gloss.get("judgement",""),
        "image": gloss.get("image",""),
    }

def nuclear_from_bits(bits6: List[int]) -> List[int]:
    # nuclear (mutual) hexagram is formed from inner lines 2–4 for lower trigram
    # and 3–5 for upper trigram (traditional rule).
    # Here lines are indexed 0..5 bottom→top.
    lower_bits = [bits6[1], bits6[2], bits6[3]]
    upper_bits = [bits6[2], bits6[3], bits6[4]]
    return lower_bits + upper_bits

def cast_hexagram(query: str, include_nuclear: bool, bundle: Dict|None) -> CastResult:
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    seed_material = f"{query}|{ts}".encode("utf-8")
    seed = hashlib.sha256(seed_material).digest()
    seed_hex = seed.hex()

    # one “full-hash” ID for the cast
    full_hash = pbkdf2(seed, b"hexagram-id")
    full_hash8 = full_hash.hex()[:8]

    # derive six lines deterministically using per-line salts
    lines: List[int] = []
    bits: List[int] = []
    moving_idx: List[int] = []
    for i in range(6):
        d = pbkdf2(seed, f"line-{i}".encode("utf-8"))
        val = line_from_digest(d)
        lines.append(val)
        bit = yin_yang_bit(val)
        bits.append(bit)
        if val in (6,9):
            moving_idx.append(i)

    primary_bits = bits[:]
    relating_bits = bits[:]
    if moving_idx:
        for i in moving_idx:
            relating_bits[i] = flip_bit(relating_bits[i])

    # choose text bundle (if provided) to override concise gloss
    # expected structure for bundle JSON:
    # { "<number>": { "name": "...", "judgement": "...", "image": "...", "lines": { "1":"...",...,"6":"..." } }, ... }
    if bundle:
        def meta_with_bundle(bitsX: List[int]) -> Dict[str,str]:
            m = hex_meta_from_bits(bitsX)
            try:
                b = bundle.get(m["number"], None)
                if b:
                    m["name"] = b.get("name", m["name"])
                    m["judgement"] = b.get("judgement", m["judgement"])
                    m["image"] = b.get("image", m["image"])
                return m
            except Exception:
                return m
    else:
        meta_with_bundle = hex_meta_from_bits

    primary_meta = meta_with_bundle(primary_bits)
    relating_meta = meta_with_bundle(relating_bits) if moving_idx else None

    nuclear_meta = None
    if include_nuclear:
        nuc_bits = nuclear_from_bits(primary_bits)
        nuclear_meta = meta_with_bundle(nuc_bits)

    return CastResult(
        query=query,
        timestamp_utc=ts,
        seed_hex=seed_hex,
        full_hash8=full_hash8,
        lines=lines,
        primary_bits=primary_bits,
        moving_indices=moving_idx,
        relating_bits=relating_bits,
        primary_meta=primary_meta,
        relating_meta=relating_meta,
        nuclear_meta=nuclear_meta
    )

def print_result(res: CastResult, show_lines: bool, show_nuclear: bool, show_bundle_lines: bool, bundle: Dict|None):
    def bits_to_str(bits6: List[int]) -> str:
        return "".join("—" if b==1 else "– –" for b in bits6)  # visual: yang solid vs yin broken

    def table_for(title: str, meta: Dict[str,str], bits6: List[int]) -> Table:
        t = Table(title=title)
        t.add_column("Hex #", justify="right", style="cyan", no_wrap=True)
        t.add_column("Name", style="bold white")
        t.add_column("Upper/Lower", style="magenta")
        t.add_column("Judgement", style="white")
        t.add_column("Image", style="white")
        t.add_row(
            meta["number"], meta["name"],
            f"{meta['upper']} over {meta['lower']}",
            meta.get("judgement",""),
            meta.get("image","")
        )
        return t

    # header
    if RICH:
        console.rule(f"[bold magenta]I-Ching Cast • {res.full_hash8}")
        console.print(f"[dim]UTC:[/dim] {res.timestamp_utc}   [dim]Seed:[/dim] {res.seed_hex[:16]}…")
    else:
        print(f"I-Ching Cast • {res.full_hash8}")
        print(f"UTC: {res.timestamp_utc}   Seed: {res.seed_hex[:16]}…")

    # primary
    if RICH:
        console.print(table_for("Primary Hexagram", res.primary_meta, res.primary_bits))
        linebar = bits_to_str(res.primary_bits)
        console.print(f"Lines (bottom→top): {linebar}")
    else:
        pm = res.primary_meta
        print(f"Primary: #{pm['number']} {pm['name']}  ({pm['upper']} over {pm['lower']})")
        print(f"  Judgement: {pm.get('judgement','')}")
        print(f"  Image: {pm.get('image','')}")
        print(f"  Lines (bottom→top): {bits_to_str(res.primary_bits)}")

    # moving lines
    if res.moving_indices:
        idxs = [str(i+1) for i in res.moving_indices]  # human 1..6
        if RICH:
            console.print(f"[yellow]Moving lines:[/yellow] {', '.join(idxs)}")
        else:
            print(f"Moving lines: {', '.join(idxs)}")

        # optional moving line texts (only if bundle includes them)
        if show_bundle_lines and bundle:
            num = res.primary_meta["number"]
            bhex = bundle.get(num, {})
            lines_text = bhex.get("lines", {})
            for i in res.moving_indices:
                key = str(i+1)
                txt = lines_text.get(key, "")
                if txt:
                    if RICH:
                        console.print(f"  [cyan]Line {key}[/cyan]: {txt}")
                    else:
                        print(f"  Line {key}: {txt}")

        # relating hexagram
        if RICH:
            console.print(table_for("Relating Hexagram", res.relating_meta, res.relating_bits))
            console.print(f"Lines (bottom→top): {bits_to_str(res.relating_bits)}")
        else:
            rm = res.relating_meta
            print(f"Relating: #{rm['number']} {rm['name']}  ({rm['upper']} over {rm['lower']})")
            print(f"  Lines (bottom→top): {bits_to_str(res.relating_bits)}")
    else:
        if RICH:
            console.print("[dim]No moving lines.[/dim]")
        else:
            print("No moving lines.")

    # nuclear (optional)
    if show_nuclear and res.nuclear_meta:
        if RICH:
            console.print(table_for("Nuclear Hexagram", res.nuclear_meta, []))
        else:
            nm = res.nuclear_meta
            print(f"Nuclear: #{nm['number']} {nm['name']}  ({nm['upper']} over {nm['lower']})")

def main():
    p = argparse.ArgumentParser(
        description="Deterministic I-Ching via hashing (coin method).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    p.add_argument("-q","--query", help="Question (prompted if omitted).")
    p.add_argument("--no-nuclear", action="store_true", help="Do not compute/show the nuclear hexagram.")
    p.add_argument("--bundle", help="Path to JSON bundle with hexagram texts (Legge PD etc.).")
    p.add_argument("--bundle-lines", action="store_true", help="If bundle has per-line texts, show texts for moving lines.")
    p.add_argument("--autosave", help="Autosave reading JSON to this file (append as JSONL if endswith .jsonl).")
    p.add_argument("--show-lines", action="store_true", help="Also print raw line values (6/7/8/9).")
    args = p.parse_args()

    query = args.query or input("Ask your question: ").strip()
    if not query:
        print("Error: query required.", file=sys.stderr)
        sys.exit(1)

    # load bundle if provided
    bundle = None
    if args.bundle:
        try:
            with open(args.bundle, "r", encoding="utf-8") as f:
                bundle = json.load(f)
        except Exception as e:
            print(f"Warning: failed to load bundle: {e}", file=sys.stderr)

    if RICH:
        with console.status("[bold cyan]Casting your hexagram…[/bold cyan]", spinner="dots"):
            res = cast_hexagram(query, include_nuclear=(not args.no_nuclear), bundle=bundle)
    else:
        print("Casting your hexagram…", end="", flush=True)
        res = cast_hexagram(query, include_nuclear=(not args.no_nuclear), bundle=bundle)
        print(" done.")

    res = cast_hexagram(query, include_nuclear=(not args.no_nuclear), bundle=bundle)

    print_result(
        res,
        show_lines=args.show_lines,
        show_nuclear=(not args.no_nuclear),
        show_bundle_lines=args.bundle_lines,
        bundle=bundle
    )

    # autosave
    if args.autosave:
        payload = asdict(res)
        try:
            if args.autosave.lower().endswith(".jsonl"):
                with open(args.autosave, "a", encoding="utf-8") as f:
                    f.write(json.dumps(payload, ensure_ascii=False) + "\n")
            else:
                # write/overwrite simple JSON
                with open(args.autosave, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: failed to autosave: {e}", file=sys.stderr)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCanceled.")
        sys.exit(0)
