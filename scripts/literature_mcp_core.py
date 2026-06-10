from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def load_corpus(corpus_path: Path) -> list[dict[str, Any]]:
    if not corpus_path.exists():
        return []
    rows = []
    with corpus_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def evidence_boundary(status: str) -> str:
    if status == "fulltext-read":
        return "May support factual writing claims if the specific extracted evidence matches the draft sentence."
    if status == "abstract-screened":
        return "Use for candidate framing or style examples only; do not use as full-paper evidence."
    if status == "metadata-only":
        return "Use for discovery or style examples only; do not use as factual evidence."
    if status == "citation-chain":
        return "Use only as a citation-network lead until screened."
    if status == "excluded":
        return "Do not use for positive review claims."
    return "Evidence status is missing or unknown; verify before use."


def annotate_boundary(row: dict[str, Any]) -> dict[str, Any]:
    copy = dict(row)
    copy["usage_boundary"] = evidence_boundary(str(row.get("evidence_status", "")))
    return copy


def score_row(row: dict[str, Any], terms: list[str]) -> int:
    text = " ".join(str(row.get(key, "")) for key in ["sentence", "title", "journal", "section"]).lower()
    return sum(1 for term in terms if term and term in text)


def search_rows(corpus_path: Path, query: str, limit: int = 8, evidence_status: str = "") -> list[dict[str, Any]]:
    terms = [term.lower() for term in re.findall(r"[A-Za-z0-9-]+", query)]
    rows = load_corpus(corpus_path)
    if evidence_status:
        rows = [row for row in rows if row.get("evidence_status") == evidence_status]
    ranked = [(score_row(row, terms), row) for row in rows]
    ranked = [(score, row) for score, row in ranked if score > 0 or not terms]
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [annotate_boundary(row) for _, row in ranked[:limit]]


def phrase_suggestions(corpus_path: Path, rhetorical_function: str, limit: int) -> list[dict[str, str]]:
    aliases = {
        "background": "background-motivation",
        "gap": "gap-or-limitation",
        "limitation": "gap-or-limitation",
        "method": "method-positioning",
        "result": "result-reporting",
    }
    normalized = aliases.get(rhetorical_function, rhetorical_function)
    rows = [
        row
        for row in load_corpus(corpus_path)
        if row.get("rhetorical_function") == normalized or normalized in str(row.get("rhetorical_function", ""))
    ]
    return [
        {
            "paper_id": str(row.get("paper_id", "")),
            "title": str(row.get("title", "")),
            "journal": str(row.get("journal", "")),
            "sentence": str(row.get("sentence", "")),
            "evidence_status": str(row.get("evidence_status", "")),
            "source_note": str(row.get("source_note", "")),
            "usage_boundary": evidence_boundary(str(row.get("evidence_status", ""))),
        }
        for row in rows[:limit]
    ]
