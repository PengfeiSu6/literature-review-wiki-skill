#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


DEFAULT_DIRS = [
    "config",
    "daily",
    "papers",
    "topics",
    "claims",
    "reviews",
    "templates",
    "data",
]


def slugify(value: str) -> str:
    keep = []
    for char in value.lower():
        if char.isalnum():
            keep.append(char)
        elif char in {" ", "-", "_", "/", ":"}:
            keep.append("-")
    slug = "".join(keep)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "literature-topic"


def write_if_missing(path: Path, content: str, overwrite: bool = False) -> bool:
    if path.exists() and not overwrite:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def build_config(args: argparse.Namespace) -> dict:
    topic_slug = slugify(args.topic)
    return {
        "topic": args.topic,
        "topic_slug": topic_slug,
        "created": date.today().isoformat(),
        "language": args.language,
        "zotero_collection": args.zotero_collection or args.topic,
        "wiki_root": str(Path(args.root).resolve()),
        "sources": {
            "openalex": True,
            "semantic_scholar": True,
            "crossref": True,
            "arxiv": True,
            "pubmed": False,
            "paper_search_mcp": "optional",
            "arxiv_daily_summarizer": "optional",
        },
        "daily_monitoring": {
            "enabled": False,
            "timezone": args.timezone,
            "feed_json": "",
            "lookback_days": 3,
            "max_new_papers": 50,
        },
        "evidence_statuses": [
            "metadata-only",
            "abstract-screened",
            "fulltext-read",
            "citation-chain",
            "excluded",
        ],
        "inclusion_criteria": [],
        "exclusion_criteria": [],
        "query_facets": [],
    }


def dashboard(topic: str) -> str:
    today = date.today().isoformat()
    return f"""# {topic} Literature Dashboard

## Status

- Created: {today}
- Zotero collection:
- Current review:
- Next action:

## Daily Updates

```dataview
TABLE added, source, evidence_status
FROM "Literature/papers"
SORT added DESC
```

## Topics

## Claims

## Review Drafts

- [[reviews/working-review|Working Review]]
- [[reviews/gaps|Gaps]]
- [[reviews/search-log|Search Log]]
- [[reviews/screening-log|Screening Log]]
"""


def paper_template() -> str:
    return """---
type: paper
paper_id: ""
title: ""
authors: []
year:
source: ""
journal: ""
doi: ""
arxiv_id: ""
pmid: ""
url: ""
pdf_url: ""
zotero_key: ""
zotero_status: pending
evidence_status: metadata-only
topics: []
roles: []
added: ""
last_reviewed: ""
---

# {{title}}

## Status

- Evidence status:
- Zotero:
- Next action:

## Abstract Summary

## Why It Matters

## Methods

## Evidence Extracted

## Limitations

## Links

- Source:
- PDF:
- Zotero:

## Review Use

- Can support:
- Cannot support yet:
"""


def simple_page(title: str, body: str = "") -> str:
    return f"# {title}\n\n{body}".rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize an Obsidian literature review wiki.")
    parser.add_argument("--root", required=True, help="Wiki root directory, often <vault>/Literature.")
    parser.add_argument("--topic", required=True, help="Literature review topic.")
    parser.add_argument("--language", default="zh-CN", help="Review output language.")
    parser.add_argument("--timezone", default="Asia/Shanghai", help="Daily monitoring timezone.")
    parser.add_argument("--zotero-collection", default="", help="Zotero collection name.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite starter files.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    for dirname in DEFAULT_DIRS:
        (root / dirname).mkdir(parents=True, exist_ok=True)

    config = build_config(args)
    written = []
    config_path = root / "config" / "literature-review-config.json"
    if write_if_missing(config_path, json.dumps(config, ensure_ascii=False, indent=2) + "\n", args.overwrite):
        written.append(config_path)

    starters = {
        root / "dashboard.md": dashboard(args.topic),
        root / "templates" / "paper-template.md": paper_template(),
        root / "reviews" / "working-review.md": simple_page("Working Review", "## Current Synthesis\n\n## Evidence Boundary\n"),
        root / "reviews" / "gaps.md": simple_page("Research Gaps", "## Candidate Gaps\n\n## Evidence Needed\n"),
        root / "reviews" / "search-log.md": simple_page("Search Log", "## Searches\n\n"),
        root / "reviews" / "screening-log.md": simple_page("Screening Log", "## Included\n\n## Excluded\n"),
        root / "data" / "seen_papers.json": "{}\n",
    }
    for path, content in starters.items():
        if write_if_missing(path, content, args.overwrite):
            written.append(path)

    print(f"Initialized literature wiki at {root}")
    if written:
        print("Wrote:")
        for path in written:
            print(f"  {path}")
    else:
        print("No files overwritten. Use --overwrite to refresh starter files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
