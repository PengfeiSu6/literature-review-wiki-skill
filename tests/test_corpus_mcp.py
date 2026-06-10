from __future__ import annotations

from pathlib import Path

from scripts.build_corpus import build_corpus, split_sentences
from scripts.literature_mcp_core import evidence_boundary, phrase_suggestions, search_rows


def write_note(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """---
type: paper
paper_id: "fixture-paper"
title: "Industrial flexibility paper"
journal: "Applied Energy"
year: "2026"
doi: "10.0000/fixture"
url: "https://doi.org/10.0000/fixture"
evidence_status: metadata-only
pdf_path: ""
---

# Industrial flexibility paper

## Abstract Summary

Industrial energy flexibility has become increasingly important for renewable integration. This paper presents a scheduling framework for flexible industrial loads. Results show that coordinated operation can reduce peak demand.

## Evidence Extracted

""",
        encoding="utf-8",
    )


def test_sentence_split_keeps_basic_academic_sentences() -> None:
    assert split_sentences("This paper presents a method. Results show improvements.") == [
        "This paper presents a method.",
        "Results show improvements.",
    ]


def test_build_corpus_and_search_rows(tmp_path: Path) -> None:
    vault = tmp_path / "Literature"
    write_note(vault / "papers" / "fixture-paper.md")

    summary = build_corpus(vault)
    corpus_path = Path(summary["sentences_path"])

    assert summary["sentences"] == 3
    rows = search_rows(corpus_path, "renewable integration", limit=2)
    assert rows
    assert rows[0]["paper_id"] == "fixture-paper"
    assert "style examples only" in rows[0]["usage_boundary"]


def test_phrase_suggestions_and_evidence_boundary(tmp_path: Path) -> None:
    vault = tmp_path / "Literature"
    write_note(vault / "papers" / "fixture-paper.md")
    summary = build_corpus(vault)

    suggestions = phrase_suggestions(Path(summary["sentences_path"]), "method", 5)

    assert suggestions
    assert suggestions[0]["source_note"]
    assert "style examples only" in evidence_boundary("metadata-only")
