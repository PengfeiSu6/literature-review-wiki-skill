#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def first_present(record: dict[str, Any], keys: list[str], default: str = "") -> str:
    for key in keys:
        value = record.get(key)
        if value is None:
            continue
        if isinstance(value, list):
            return ", ".join(str(item) for item in value if item)
        text = str(value).strip()
        if text:
            return text
    return default


def extract_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    candidates = []
    for key in ["records", "papers", "items", "results", "selected_records", "daily_papers"]:
        value = payload.get(key)
        if isinstance(value, list):
            candidates.extend(item for item in value if isinstance(item, dict))
    sections = payload.get("sections")
    if isinstance(sections, list):
        for section in sections:
            if isinstance(section, dict):
                candidates.extend(extract_records(section))
    if candidates:
        return candidates
    if "title" in payload:
        return [payload]
    return []


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:90] or "paper"


def stable_id(record: dict[str, Any]) -> str:
    doi = first_present(record, ["doi", "DOI"])
    arxiv_id = first_present(record, ["arxiv_id", "arxivId", "arxiv", "id"])
    url = first_present(record, ["url", "link", "entry_id"])
    title = first_present(record, ["title", "name"], "untitled")
    if doi:
        return "doi-" + slugify(doi)
    if arxiv_id and ("arxiv" in arxiv_id.lower() or re.search(r"\d{4}\.\d{4,5}", arxiv_id)):
        return "arxiv-" + slugify(arxiv_id)
    if url:
        digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]
        return "url-" + digest
    digest = hashlib.sha1(title.encode("utf-8")).hexdigest()[:10]
    return "title-" + digest


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    title = first_present(record, ["title", "name"], "Untitled paper")
    authors_raw = record.get("authors") or record.get("author") or record.get("creators") or []
    authors = []
    for item in as_list(authors_raw):
        if isinstance(item, dict):
            authors.append(first_present(item, ["name", "display_name", "full_name"], ""))
        else:
            authors.append(str(item))
    authors = [author for author in authors if author]
    published = first_present(record, ["published_date", "published_at", "published", "date", "year"])
    year = ""
    match = re.search(r"(19|20)\d{2}", published)
    if match:
        year = match.group(0)
    return {
        "paper_id": stable_id(record),
        "title": title,
        "authors": authors,
        "year": year,
        "source": first_present(record, ["source", "source_key", "provider"]),
        "journal": first_present(record, ["journal", "venue", "publication_venue"]),
        "doi": first_present(record, ["doi", "DOI"]),
        "arxiv_id": first_present(record, ["arxiv_id", "arxivId", "arxiv"]),
        "url": first_present(record, ["url", "link", "entry_id"]),
        "pdf_url": first_present(record, ["pdf_url", "pdfUrl", "pdf", "open_access_pdf"]),
        "published": published,
        "summary": first_present(record, ["ai_summary", "summary", "abstract", "abstract_raw", "comment"]),
        "score": first_present(record, ["final_score", "score", "rule_score"]),
        "categories": as_list(record.get("categories") or record.get("tags")),
    }


def yaml_list(values: list[str]) -> str:
    if not values:
        return "[]"
    escaped = [str(value).replace('"', '\\"') for value in values]
    return "[" + ", ".join(f'"{value}"' for value in escaped) + "]"


def yaml_scalar(value: Any) -> str:
    return str(value or "").replace("\\", "\\\\").replace('"', '\\"')


def paper_markdown(record: dict[str, Any], added: str) -> str:
    authors = yaml_list(record["authors"])
    categories = yaml_list([str(item) for item in record["categories"]])
    title = yaml_scalar(record["title"])
    year = yaml_scalar(record["year"])
    source = yaml_scalar(record["source"])
    journal = yaml_scalar(record["journal"])
    doi = yaml_scalar(record["doi"])
    arxiv_id = yaml_scalar(record["arxiv_id"])
    url = yaml_scalar(record["url"])
    pdf_url = yaml_scalar(record["pdf_url"])
    return f"""---
type: paper
paper_id: "{record['paper_id']}"
title: "{title}"
authors: {authors}
year: "{year}"
source: "{source}"
journal: "{journal}"
doi: "{doi}"
arxiv_id: "{arxiv_id}"
url: "{url}"
pdf_url: "{pdf_url}"
zotero_key: ""
zotero_status: pending
evidence_status: metadata-only
topics: {categories}
roles: [candidate]
added: "{added}"
last_reviewed: ""
---

# {record['title']}

## Status

- Evidence status: metadata-only
- Zotero: pending
- Score: {record['score']}
- Next action: screen abstract and decide whether to import into Zotero.

## Abstract Summary

{record['summary']}

## Why It Matters

## Methods

## Evidence Extracted

## Limitations

## Links

- Source: {record['url']}
- PDF: {record['pdf_url']}
- DOI: {record['doi']}

## Review Use

- Can support: candidate discovery only.
- Cannot support yet: detailed review claims until full text is read.
"""


def daily_markdown(records: list[dict[str, Any]], run_date: str, source_name: str) -> str:
    lines = [f"# Daily Literature Update - {run_date}", "", f"- Source: {source_name}", f"- New records: {len(records)}", ""]
    lines.append("## New Papers")
    lines.append("")
    for record in records:
        lines.append(f"- [[papers/{record['paper_id']}|{record['title']}]]")
    lines.append("")
    lines.append("## Triage")
    lines.append("")
    lines.append("- Import to Zotero:")
    lines.append("- Read full text:")
    lines.append("- Exclude:")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert a daily paper JSON feed into Obsidian notes.")
    parser.add_argument("--input", required=True, help="Path to JSON feed, such as site/latest.json.")
    parser.add_argument("--vault", required=True, help="Wiki root directory, often <vault>/Literature.")
    parser.add_argument("--date", default="", help="Override update date, YYYY-MM-DD.")
    parser.add_argument("--source-name", default="daily-json", help="Human-readable source name.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing paper notes.")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    root = Path(args.vault).resolve()
    run_date = args.date or date.today().isoformat()
    payload = load_json(input_path)
    records = [normalize_record(record) for record in extract_records(payload)]

    for dirname in ["daily", "papers", "data"]:
        (root / dirname).mkdir(parents=True, exist_ok=True)

    seen_path = root / "data" / "seen_papers.json"
    if seen_path.exists():
        seen = json.loads(seen_path.read_text(encoding="utf-8"))
    else:
        seen = {}

    new_records = []
    for record in records:
        paper_id = record["paper_id"]
        if paper_id in seen and not args.overwrite:
            continue
        note_path = root / "papers" / f"{paper_id}.md"
        if args.overwrite or not note_path.exists():
            note_path.write_text(paper_markdown(record, run_date), encoding="utf-8")
        seen[paper_id] = {
            "title": record["title"],
            "first_seen": seen.get(paper_id, {}).get("first_seen", run_date),
            "last_seen": run_date,
            "source": args.source_name,
        }
        new_records.append(record)

    daily_path = root / "daily" / f"{run_date}.md"
    daily_path.write_text(daily_markdown(new_records, run_date, args.source_name), encoding="utf-8")
    seen_path.write_text(json.dumps(seen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Input records: {len(records)}")
    print(f"New records: {len(new_records)}")
    print(f"Wrote daily note: {daily_path}")
    print(f"Updated seen file: {seen_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
