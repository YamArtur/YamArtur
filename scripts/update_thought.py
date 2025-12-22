from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    from zoneinfo import ZoneInfo  
except Exception:
    ZoneInfo = None  


START = "<!-- THOUGHT_OF_THE_DAY:START -->"
END = "<!-- THOUGHT_OF_THE_DAY:END -->"


@dataclass(frozen=True)
class Quote:
    text: str
    author: str
    source: str

    @staticmethod
    def from_obj(obj: dict) -> "Quote":
        text = str(obj.get("text", "")).strip()
        author = str(obj.get("author", "")).strip()
        source = str(obj.get("source", "")).strip()
        if not text:
            raise ValueError("Found a quote with empty 'text'.")
        if not author:
            author = "Unknown"
        return Quote(text=text, author=author, source=source)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _today_date_str() -> str:
    if ZoneInfo is not None:
        tz = ZoneInfo("America/Sao_Paulo")
        return datetime.now(tz).date().isoformat()
    return datetime.utcnow().date().isoformat()


def _pick_index(date_iso: str, n: int) -> int:
    y, m, d = map(int, date_iso.split("-"))
    ordinal = datetime(y, m, d).toordinal()
    return ordinal % n


def _render_block(date_iso: str, q: Quote, idx: int, n: int) -> str:
    lines = []
    lines.append(START)
    lines.append("> [!TIP]")
    lines.append(f"> **Thought of the day — {date_iso}**")
    lines.append(">")
    lines.append(f"> _“{q.text}”_")
    lines.append(">")
    lines.append(f"> — **{q.author}**")
    if q.source:
        lines.append(f"> <sub>{q.source}</sub>")
    lines.append(f"> <sub>({idx + 1}/{n}) • auto-updated daily</sub>")
    lines.append(END)
    return "\n".join(lines) + "\n"


def main() -> None:
    root = _repo_root()
    quotes_path = root / "thoughts" / "quotes.json"
    readme_path = root / "README.md"

    if not quotes_path.exists():
        raise FileNotFoundError(f"Missing {quotes_path}")
    if not readme_path.exists():
        raise FileNotFoundError(f"Missing {readme_path}")

    quotes_raw = json.loads(quotes_path.read_text(encoding="utf-8"))
    if not isinstance(quotes_raw, list) or len(quotes_raw) == 0:
        raise ValueError("quotes.json must be a non-empty JSON array.")

    quotes: list[Quote] = [Quote.from_obj(o) for o in quotes_raw]

    date_iso = _today_date_str()
    idx = _pick_index(date_iso, len(quotes))
    q = quotes[idx]

    new_block = _render_block(date_iso, q, idx, len(quotes))

    readme = readme_path.read_text(encoding="utf-8")

    pattern = re.compile(
        re.escape(START) + r".*?" + re.escape(END),
        flags=re.DOTALL
    )

    if not pattern.search(readme):
        raise RuntimeError(
            "Markers not found in README.md. "
            "Make sure you have:\n"
            f"{START}\n...\n{END}"
        )

    updated = pattern.sub(new_block.strip(), readme).rstrip() + "\n"
    if updated != readme:
        readme_path.write_text(updated, encoding="utf-8")
        print(f"Updated README.md with quote #{idx + 1}/{len(quotes)} for {date_iso}.")
    else:
        print("README.md already up to date; no changes made.")


if __name__ == "__main__":
    main()
