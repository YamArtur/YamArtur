#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, date
from pathlib import Path

START = "<!-- THOUGHT_OF_THE_DAY:START -->"
END   = "<!-- THOUGHT_OF_THE_DAY:END -->"

ROOT = Path(__file__).resolve().parents[1]
QUOTES = ROOT / "thoughts" / "quotes.json"
README = ROOT / "README.md"

def load_quotes():
    data = json.loads(QUOTES.read_text(encoding="utf-8"))
    if not isinstance(data, list) or len(data) == 0:
        raise RuntimeError("thoughts/quotes.json must be a non-empty list.")
    return data

def day_index(d: date) -> int:
    epoch = date(1970, 1, 1)
    return (d - epoch).days

def pick(quotes):
    today = datetime.utcnow().date()  # cron é UTC; mantém consistente
    q = quotes[day_index(today) % len(quotes)]
    return q, today.isoformat()

def format_block(q, day_str: str) -> str:
    text = (q.get("text") or "").strip()
    author = (q.get("author") or "").strip()
    source = (q.get("source") or "").strip()
    if not text:
        raise RuntimeError("Each entry must have a non-empty 'text'.")

    out = []
    out.append(f"**Thought of the day** — `{day_str}`")
    out.append("")
    out.append(f"> {text}")
    if author or source:
        tail = author
        if source:
            tail = (tail + " — " if tail else "") + f"*{source}*"
        out.append("")
        out.append(f"<sub>{tail}</sub>")
    return "\n".join(out).strip() + "\n"

def replace(readme: str, content: str) -> str:
    if START not in readme or END not in readme:
        raise RuntimeError("README.md is missing THOUGHT_OF_THE_DAY markers.")
    before = readme.split(START)[0]
    after = readme.split(END)[1]
    return before + START + "\n" + content + END + after

def main():
    quotes = load_quotes()
    q, day = pick(quotes)
    new_block = "\n\n" + format_block(q, day) + "\n"
    txt = README.read_text(encoding="utf-8")
    updated = replace(txt, new_block)
    if updated != txt:
        README.write_text(updated, encoding="utf-8")

if __name__ == "__main__":
    main()
