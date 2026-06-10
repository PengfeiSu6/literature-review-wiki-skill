from __future__ import annotations

from pathlib import Path

from scripts.build_corpus import build_corpus
from scripts.lint_lit_review_wiki import lint_vault
from tests.test_corpus_mcp import write_note


def test_lint_require_corpus_reports_missing(tmp_path: Path) -> None:
    root = tmp_path / "Literature"
    for dirname in ["config", "daily", "papers", "pdfs", "topics", "claims", "reviews", "templates", "data"]:
        (root / dirname).mkdir(parents=True, exist_ok=True)
    (root / "reviews" / "working-review.md").write_text("# Working Review\n", encoding="utf-8")

    issues, stats = lint_vault(root, require_corpus=True)

    assert stats["paper_notes"] == 0
    assert any("sentences.jsonl" in issue for issue in issues)


def test_lint_checks_corpus_rows(tmp_path: Path) -> None:
    root = tmp_path / "Literature"
    for dirname in ["config", "daily", "pdfs", "topics", "claims", "reviews", "templates"]:
        (root / dirname).mkdir(parents=True, exist_ok=True)
    (root / "reviews" / "working-review.md").write_text("# Working Review\n", encoding="utf-8")
    write_note(root / "papers" / "fixture-paper.md")
    build_corpus(root)

    issues, stats = lint_vault(root, require_corpus=True)

    assert issues == []
    assert stats["paper_notes"] == 1
    assert stats["corpus_rows"] == 3
