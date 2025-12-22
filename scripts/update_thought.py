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
    tz = ZoneInfo("America/Sao_Paulo")
    today = datetime.now(tz).date()

    idx = today.toordinal() % len(quotes)
    return today, quotes[idx]


def render_block(today: date, quote: dict) -> str:
    text = quote["text"].replace("\n", " ").strip()
    author = quote.get("author", "").strip()
    source = quote.get("source", "").strip()

    lines = []
    lines.append(f'> *“{text}”*  ')

    if author:
        lines.append(f'> **— {author}**  ')
    else:
        lines.append(f'> **— Unknown**  ')

    if source:
        lines.append(f'> *{source}*  ')

    lines.append(f'> <sub>Auto-updated daily • {today.isoformat()}</sub>')
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
