from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_DIRS = ["config", "daily", "papers", "topics", "claims", "reviews", "templates", "data"]
VALID_EVIDENCE = {"metadata-only", "abstract-screened", "fulltext-read", "citation-chain", "excluded"}


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint an Obsidian literature review wiki.")
    parser.add_argument("--vault", required=True, help="Wiki root directory.")
    args = parser.parse_args()

    root = Path(args.vault).resolve()
    issues = []

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

    working_review = root / "reviews" / "working-review.md"
    if not working_review.exists():
        issues.append("Missing reviews/working-review.md")

    if issues:
        print("Literature wiki lint found issues:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print(f"Literature wiki lint passed: {root}")
    print(f"Paper notes checked: {len(seen_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
