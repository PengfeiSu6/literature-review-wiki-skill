#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_DIRS = ["config", "daily", "papers", "pdfs", "topics", "claims", "reviews", "templates", "data"]
VALID_EVIDENCE = {"metadata-only", "abstract-screened", "fulltext-read", "citation-chain", "excluded"}
CORPUS_FIELDS = {"paper_id", "title", "journal", "evidence_status", "section", "rhetorical_function", "sentence", "source_note"}


def section_body(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\s*$"
    match = re.search(pattern, text, re.M)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.M)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    block = text[4:end]
    result = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"')
    return result


def lint_vault(root: Path, require_corpus: bool = False) -> tuple[list[str], dict[str, int]]:
    root = root.resolve()
    issues = []
    stats = {"paper_notes": 0, "corpus_rows": 0}

    if not root.exists():
        issues.append(f"Wiki root does not exist: {root}")
    for dirname in REQUIRED_DIRS:
        if not (root / dirname).exists():
            issues.append(f"Missing required directory: {dirname}")

    seen_ids = {}
    papers_dir = root / "papers"
    if papers_dir.exists():
        for path in papers_dir.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            fm = frontmatter(text)
            paper_id = fm.get("paper_id") or path.stem
            if paper_id in seen_ids:
                issues.append(f"Duplicate paper_id {paper_id}: {seen_ids[paper_id]} and {path}")
            seen_ids[paper_id] = path

            evidence = fm.get("evidence_status", "")
            if evidence and evidence not in VALID_EVIDENCE:
                issues.append(f"{path.name}: invalid evidence_status '{evidence}'")

            url = fm.get("url", "")
            doi = fm.get("doi", "")
            arxiv = fm.get("arxiv_id", "")
            if not any([url, doi, arxiv]):
                issues.append(f"{path.name}: missing stable source link/DOI/arXiv ID")

            if evidence != "fulltext-read" and section_body(text, "Evidence Extracted"):
                issues.append(f"{path.name}: evidence extracted while status is {evidence or 'missing'}")
        stats["paper_notes"] = len(seen_ids)

    working_review = root / "reviews" / "working-review.md"
    if not working_review.exists():
        issues.append("Missing reviews/working-review.md")

    corpus_path = root / "data" / "corpus" / "sentences.jsonl"
    if require_corpus and not corpus_path.exists():
        issues.append("Missing data/corpus/sentences.jsonl; run build_corpus.py before starting MCP.")
    if corpus_path.exists():
        with corpus_path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    issues.append(f"sentences.jsonl:{line_no}: invalid JSON: {exc}")
                    continue
                stats["corpus_rows"] += 1
                missing = sorted(field for field in CORPUS_FIELDS if not str(row.get(field, "")).strip())
                if missing:
                    issues.append(f"sentences.jsonl:{line_no}: missing MCP corpus fields: {', '.join(missing)}")
                evidence = str(row.get("evidence_status", "")).strip()
                if evidence and evidence not in VALID_EVIDENCE:
                    issues.append(f"sentences.jsonl:{line_no}: invalid evidence_status '{evidence}'")
    return issues, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint an Obsidian literature review wiki.")
    parser.add_argument("--vault", required=True, help="Wiki root directory.")
    parser.add_argument("--require-corpus", action="store_true", help="Fail if MCP corpus files are missing.")
    args = parser.parse_args()

    root = Path(args.vault).resolve()
    issues, stats = lint_vault(root, require_corpus=args.require_corpus)

    if issues:
        print("Literature wiki lint found issues:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print(f"Literature wiki lint passed: {root}")
    print(f"Paper notes checked: {stats['paper_notes']}")
    print(f"Corpus rows checked: {stats['corpus_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
