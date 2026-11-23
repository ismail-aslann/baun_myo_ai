"""Bilgi paketi: knowledge/ klasöründeki .md dosyalarını okur ve sistem istemine ekler."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"


@dataclass(frozen=True)
class Doc:
    name: str
    title: str
    text: str


@lru_cache(maxsize=1)
def load_docs() -> tuple[Doc, ...]:
    docs = []
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        first = text.splitlines()[0] if text else path.stem
        title = first.lstrip("# ").strip() or path.stem
        docs.append(Doc(name=path.stem, title=title, text=text))
    return tuple(docs)


def knowledge_text() -> str:
    parts = [f"<belge ad=\"{d.name}\">\n{d.text}\n</belge>" for d in load_docs()]
    return "\n\n".join(parts)


def summary() -> list[dict]:
    return [{"name": d.name, "title": d.title, "chars": len(d.text)} for d in load_docs()]
