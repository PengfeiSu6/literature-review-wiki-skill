#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_SECTIONS = ["Abstract Summary", "Why It Matters", "Methods", "Evidence Extracted", "Limitations"]


def frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    result: dict[str, Any] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"')
    return result


def section_body(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\s*$", text, re.M)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.M)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)
    return [part.strip() for part in parts if part.strip()]


def word_count(sentence: str) -> int:
    return len(re.findall(r"[A-Za-z][A-Za-z-]*", sentence))


def rhetorical_function(sentence: str) -> str:
    lower = sentence.lower()
    if any(marker in lower for marker in ["we propose", "this paper proposes", "this paper presents", "we present", "this study presents"]):
        return "method-positioning"
    if any(marker in lower for marker in ["results show", "results demonstrate", "experiments show", "we show that"]):
        return "result-reporting"
    if any(marker in lower for marker in ["however", "nevertheless", "remain", "lack of", "limited", "challenge"]):
        return "gap-or-limitation"
    if any(marker in lower for marker in ["has become", "is critical", "plays an important role", "increasingly"]):
        return "background-motivation"
    if any(marker in lower for marker in ["future work", "limitation", "cannot", "unable to"]):
        return "limitation"
    return "general-academic"


def load_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return ""
    try:
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        return ""


def note_records(path: Path, include_pdf_text: bool, min_words: int) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    fm = frontmatter(text)
    paper_id = fm.get("paper_id") or path.stem
    evidence = fm.get("evidence_status", "metadata-only")
    rows: list[dict[str, Any]] = []
    for section in DEFAULT_SECTIONS:
        for sentence in split_sentences(section_body(text, section)):
            if word_count(sentence) < min_words:
                continue
            rows.append(
                {
                    "paper_id": paper_id,
                    "title": fm.get("title", ""),
                    "journal": fm.get("journal", ""),
                    "year": fm.get("year", ""),
                    "evidence_status": evidence,
                    "section": section,
                    "rhetorical_function": rhetorical_function(sentence),
                    "sentence": sentence,
                    "source_note": str(path),
                }
            )
    pdf_path = fm.get("pdf_path", "")
    if include_pdf_text and pdf_path:
        pdf_text = load_pdf_text(Path(pdf_path))
        for sentence in split_sentences(pdf_text):
            if word_count(sentence) < min_words:
                continue
            rows.append(
                {
                    "paper_id": paper_id,
                    "title": fm.get("title", ""),
                    "journal": fm.get("journal", ""),
                    "year": fm.get("year", ""),
                    "evidence_status": evidence,
                    "section": "PDF text",
                    "rhetorical_function": rhetorical_function(sentence),
                    "sentence": sentence,
                    "source_note": str(path),
                }
            )
    return rows


def phrase_key(sentence: str) -> str:
    words = re.findall(r"[A-Za-z][A-Za-z-]*", sentence)
    return " ".join(words[:6]).lower()


def write_phrase_report(rows: list[dict[str, Any]], path: Path) -> None:
    by_function: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        key = phrase_key(row["sentence"])
        if len(key.split()) >= 3:
            by_function[row["rhetorical_function"]][key] += 1
    lines = ["# Corpus Phrase Patterns", "", "Use these as style evidence, not as claims about paper findings.", ""]
    for function_name, counter in sorted(by_function.items()):
        lines.append(f"## {function_name}")
        lines.append("")
        for phrase, count in counter.most_common(20):
            lines.append(f"- `{phrase}` ({count})")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_corpus(vault: Path, include_pdf_text: bool = False, min_words: int = 8) -> dict[str, Any]:
    root = vault.resolve()
    papers_dir = root / "papers"
    corpus_dir = root / "data" / "corpus"
    corpus_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for note in sorted(papers_dir.glob("*.md")):
        rows.extend(note_records(note, include_pdf_text=include_pdf_text, min_words=min_words))
    sentences_path = corpus_dir / "sentences.jsonl"
    with sentences_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    phrase_path = corpus_dir / "phrase-patterns.md"
    write_phrase_report(rows, phrase_path)
    return {"sentences": len(rows), "sentences_path": str(sentences_path), "phrase_path": str(phrase_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a sentence-level writing corpus from Obsidian paper notes and optional PDFs.")
    parser.add_argument("--vault", required=True, help="Wiki root directory, often <vault>/Literature.")
    parser.add_argument("--include-pdf-text", action="store_true", help="Use pypdf to extract local PDF text when pdf_path exists.")
    parser.add_argument("--min-words", type=int, default=8, help="Minimum English word count per sentence.")
    args = parser.parse_args()
    print(json.dumps(build_corpus(Path(args.vault), args.include_pdf_text, args.min_words), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
