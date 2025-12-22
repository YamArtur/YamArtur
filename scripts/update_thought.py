#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import sys
import html
from datetime import datetime, date
from zoneinfo import ZoneInfo
from pathlib import Path

README_PATH = Path("README.md")
QUOTES_PATH = Path("thoughts/quotes.json")

START = "<!-- THOUGHT_OF_THE_DAY:START -->"
END = "<!-- THOUGHT_OF_THE_DAY:END -->"


def load_quotes(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Quotes file not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, list) or len(data) == 0:
        raise ValueError("quotes.json must be a non-empty JSON array.")

    # Basic validation
    cleaned = []
    for i, q in enumerate(data):
        if not isinstance(q, dict):
            raise ValueError(f"Entry {i} is not an object.")
        text = str(q.get("text", "")).strip()
        author = str(q.get("author", "")).strip()
        source = str(q.get("source", "")).strip()
        if not text:
            raise ValueError(f"Entry {i} has empty 'text'.")
        cleaned.append({"text": text, "author": author, "source": source})

    return cleaned


def pick_quote(quotes):
    # Use São Paulo local date so it "feels daily" for you.
    tz = ZoneInfo("America/Sao_Paulo")
    today = datetime.now(tz).date()

    # Deterministic daily index, cycles forever:
    idx = today.toordinal() % len(quotes)
    return today, quotes[idx]


def render_block(today: date, quote: dict) -> str:
    text = quote["text"].replace("\n", " ").strip()
    author = quote["author"].strip()
    source = quote["source"].strip()

    # Escape to avoid HTML injection issues
    text_esc = html.escape(text)
    author_esc = html.escape(author) if author else ""
    source_esc = html.escape(source) if source else ""

    # Pretty, centered “card-like” layout (no table borders):
    lines = []
    lines.append('<div align="center">')
    lines.append(f'  <p><i>“{text_esc}”</i></p>')

    meta = []
    if author_esc:
        meta.append(f"<b>— {author_esc}</b>")
    if source_esc:
        meta.append(f"<sub>{source_esc}</sub>")

    if meta:
        # put author then source in separate lines
        lines.append("  <p>")
        lines.append("    " + "<br/>\n    ".join(meta))
        lines.append("  </p>")

    lines.append(f'  <sub>Updated: {today.isoformat()} (America/Sao_Paulo)</sub>')
    lines.append("</div>")

    return "\n".join(lines)


def update_readme(readme_text: str, new_block: str) -> str:
    if START not in readme_text or END not in readme_text:
        raise ValueError(f"README markers not found. Expected {START} and {END}.")

    pattern = re.compile(
        re.escape(START) + r".*?" + re.escape(END),
        flags=re.DOTALL
    )

    replacement = START + "\n" + new_block + "\n" + END
    return pattern.sub(replacement, readme_text, count=1)


def main():
    quotes = load_quotes(QUOTES_PATH)
    today, q = pick_quote(quotes)
    block = render_block(today, q)

    readme = README_PATH.read_text(encoding="utf-8")
    updated = update_readme(readme, block)

    if updated != readme:
        README_PATH.write_text(updated, encoding="utf-8")
        print(f"README updated with quote of {today.isoformat()}.")
    else:
        print("No changes needed (already up to date).")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
