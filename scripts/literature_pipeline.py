#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


USER_AGENT = "literature-review-wiki-skill/0.2 (+https://github.com/PengfeiSu6/literature-review-wiki-skill)"
VALID_EVIDENCE = {"metadata-only", "abstract-screened", "fulltext-read", "citation-chain", "excluded"}


@dataclass
class PaperRecord:
    paper_id: str
    title: str
    authors: list[str] = field(default_factory=list)
    year: str = ""
    source: str = ""
    journal: str = ""
    doi: str = ""
    arxiv_id: str = ""
    pmid: str = ""
    url: str = ""
    pdf_url: str = ""
    published: str = ""
    abstract: str = ""
    discovery_source: str = ""
    discovery_query: str = ""
    venue_match: bool = False
    topics: list[str] = field(default_factory=list)
    pdf_path: str = ""

    def dedupe_key(self) -> str:
        if self.doi:
            return "doi:" + normalize_key(self.doi)
        if self.arxiv_id:
            return "arxiv:" + normalize_key(self.arxiv_id)
        return "title:" + normalize_key(self.title)

    def as_dict(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "source": self.source,
            "journal": self.journal,
            "doi": self.doi,
            "arxiv_id": self.arxiv_id,
            "pmid": self.pmid,
            "url": self.url,
            "pdf_url": self.pdf_url,
            "published": self.published,
            "abstract": self.abstract,
            "discovery_source": self.discovery_source,
            "discovery_query": self.discovery_query,
            "venue_match": self.venue_match,
            "topics": self.topics,
            "pdf_path": self.pdf_path,
        }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def slugify(value: str, max_len: int = 90) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:max_len].strip("-") or "paper"


def stable_id(title: str, doi: str = "", arxiv_id: str = "", url: str = "") -> str:
    if doi:
        return "doi-" + slugify(doi)
    if arxiv_id:
        return "arxiv-" + slugify(arxiv_id)
    if url:
        return "url-" + hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
    return "title-" + hashlib.sha1(title.encode("utf-8")).hexdigest()[:12]


def plain_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(plain_text(item) for item in value if item)
    text = str(value)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def first_present(record: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        value = record.get(key)
        text = plain_text(value)
        if text:
            return text
    return ""


def http_json(url: str, timeout: int = 30) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def http_text(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def abstract_from_openalex(inverted_index: dict[str, list[int]] | None) -> str:
    if not inverted_index:
        return ""
    positions: list[tuple[int, str]] = []
    for word, indexes in inverted_index.items():
        for index in indexes:
            positions.append((int(index), word))
    return " ".join(word for _, word in sorted(positions))


def published_from_parts(parts: dict[str, Any] | None) -> str:
    if not parts:
        return ""
    date_parts = parts.get("date-parts") or []
    if not date_parts or not isinstance(date_parts[0], list):
        return ""
    values = [str(item).zfill(2) for item in date_parts[0] if item]
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]}-{values[1]}"
    return f"{values[0]}-{values[1]}-{values[2]}"


def year_from_date(value: str) -> str:
    match = re.search(r"(19|20)\d{2}", value or "")
    return match.group(0) if match else ""


def topic_terms(config: dict[str, Any]) -> list[str]:
    terms = [str(config.get("topic", "")).strip()]
    terms.extend(str(item).strip() for item in config.get("topic_aliases", []) if str(item).strip())
    return [term for term in terms if term]


def venue_matcher(config: dict[str, Any]):
    allowlist = {normalize_key(item) for item in config.get("included_venues", [])}
    patterns = [re.compile(item, re.I) for item in config.get("venue_patterns", [])]

    def matches(venue: str) -> bool:
        if not venue:
            return False
        normalized = normalize_key(venue)
        if normalized in allowlist:
            return True
        return any(pattern.search(venue) for pattern in patterns)

    return matches


def query_since_date(config: dict[str, Any]) -> str:
    lookback_days = int(config.get("lookback_days", 7))
    from_year = str(config.get("from_year", "")).strip()
    if from_year:
        return f"{from_year}-01-01"
    return (datetime.now(timezone.utc).date() - timedelta(days=lookback_days)).isoformat()


def search_openalex(query: str, config: dict[str, Any]) -> list[PaperRecord]:
    per_page = int(config.get("max_results_per_source", 25))
    since = query_since_date(config)
    params = {
        "search": query,
        "per-page": str(per_page),
        "sort": "publication_date:desc",
        "filter": f"from_publication_date:{since}",
    }
    if config.get("openalex_mailto"):
        params["mailto"] = str(config["openalex_mailto"])
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    payload = http_json(url)
    records = []
    for item in payload.get("results", []):
        title = plain_text(item.get("title")) or "Untitled paper"
        primary = item.get("primary_location") or {}
        source = primary.get("source") or {}
        open_access = item.get("open_access") or {}
        doi = str(item.get("doi") or "").replace("https://doi.org/", "")
        pdf_url = plain_text(primary.get("pdf_url")) or plain_text(open_access.get("oa_url"))
        authors = []
        for authorship in item.get("authorships", []):
            author = authorship.get("author") or {}
            name = plain_text(author.get("display_name"))
            if name:
                authors.append(name)
        published = plain_text(item.get("publication_date"))
        records.append(
            PaperRecord(
                paper_id=stable_id(title, doi=doi, url=plain_text(item.get("id"))),
                title=title,
                authors=authors,
                year=year_from_date(published),
                source="OpenAlex",
                journal=plain_text(source.get("display_name")),
                doi=doi,
                url=plain_text(item.get("doi")) or plain_text(item.get("id")),
                pdf_url=pdf_url,
                published=published,
                abstract=abstract_from_openalex(item.get("abstract_inverted_index")),
                discovery_source="openalex",
                discovery_query=query,
            )
        )
    return records


def search_crossref(query: str, config: dict[str, Any]) -> list[PaperRecord]:
    rows = int(config.get("max_results_per_source", 25))
    since = query_since_date(config)
    params = {
        "query.bibliographic": query,
        "rows": str(rows),
        "filter": f"from-pub-date:{since},type:journal-article",
        "sort": "published",
        "order": "desc",
    }
    if config.get("crossref_mailto"):
        params["mailto"] = str(config["crossref_mailto"])
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    payload = http_json(url)
    records = []
    for item in payload.get("message", {}).get("items", []):
        title = plain_text(item.get("title")) or "Untitled paper"
        doi = plain_text(item.get("DOI"))
        authors = []
        for author in item.get("author", []):
            name = " ".join(part for part in [author.get("given"), author.get("family")] if part)
            if name:
                authors.append(name)
        published = published_from_parts(item.get("published-print")) or published_from_parts(item.get("published-online"))
        pdf_url = ""
        for link in item.get("link", []):
            if "pdf" in plain_text(link.get("content-type")).lower() or plain_text(link.get("URL")).lower().endswith(".pdf"):
                pdf_url = plain_text(link.get("URL"))
                break
        records.append(
            PaperRecord(
                paper_id=stable_id(title, doi=doi, url=plain_text(item.get("URL"))),
                title=title,
                authors=authors,
                year=year_from_date(published),
                source="Crossref",
                journal=plain_text(item.get("container-title")),
                doi=doi,
                url=plain_text(item.get("URL")),
                pdf_url=pdf_url,
                published=published,
                abstract=plain_text(item.get("abstract")),
                discovery_source="crossref",
                discovery_query=query,
            )
        )
    return records


def search_arxiv(query: str, config: dict[str, Any]) -> list[PaperRecord]:
    max_results = int(config.get("max_results_per_source", 25))
    params = {
        "search_query": "all:" + query,
        "start": "0",
        "max_results": str(max_results),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
    xml_text = http_text(url)
    root = ET.fromstring(xml_text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    records = []
    for entry in root.findall("atom:entry", ns):
        title = plain_text(entry.findtext("atom:title", default="", namespaces=ns)) or "Untitled paper"
        entry_id = plain_text(entry.findtext("atom:id", default="", namespaces=ns))
        arxiv_id = entry_id.rstrip("/").split("/")[-1]
        authors = [plain_text(author.findtext("atom:name", default="", namespaces=ns)) for author in entry.findall("atom:author", ns)]
        authors = [author for author in authors if author]
        published = plain_text(entry.findtext("atom:published", default="", namespaces=ns))
        pdf_url = ""
        for link in entry.findall("atom:link", ns):
            if link.attrib.get("title") == "pdf":
                pdf_url = link.attrib.get("href", "")
                break
        if not pdf_url and entry_id:
            pdf_url = entry_id.replace("/abs/", "/pdf/") + ".pdf"
        records.append(
            PaperRecord(
                paper_id=stable_id(title, arxiv_id=arxiv_id, url=entry_id),
                title=title,
                authors=authors,
                year=year_from_date(published),
                source="arXiv",
                journal="arXiv",
                arxiv_id=arxiv_id,
                url=entry_id,
                pdf_url=pdf_url,
                published=published[:10],
                abstract=plain_text(entry.findtext("atom:summary", default="", namespaces=ns)),
                discovery_source="arxiv",
                discovery_query=query,
            )
        )
    return records


def search_semantic_scholar(query: str, config: dict[str, Any]) -> list[PaperRecord]:
    limit = int(config.get("max_results_per_source", 25))
    fields = "title,authors,year,venue,abstract,url,externalIds,openAccessPdf,publicationDate"
    params = {"query": query, "limit": str(limit), "fields": fields}
    url = "https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode(params)
    payload = http_json(url)
    records = []
    for item in payload.get("data", []):
        title = plain_text(item.get("title")) or "Untitled paper"
        external = item.get("externalIds") or {}
        doi = plain_text(external.get("DOI"))
        arxiv_id = plain_text(external.get("ArXiv"))
        pmid = plain_text(external.get("PubMed"))
        authors = [plain_text(author.get("name")) for author in item.get("authors", [])]
        authors = [author for author in authors if author]
        pdf = item.get("openAccessPdf") or {}
        published = plain_text(item.get("publicationDate")) or plain_text(item.get("year"))
        records.append(
            PaperRecord(
                paper_id=stable_id(title, doi=doi, arxiv_id=arxiv_id, url=plain_text(item.get("url"))),
                title=title,
                authors=authors,
                year=year_from_date(published),
                source="Semantic Scholar",
                journal=plain_text(item.get("venue")),
                doi=doi,
                arxiv_id=arxiv_id,
                pmid=pmid,
                url=plain_text(item.get("url")),
                pdf_url=plain_text(pdf.get("url")),
                published=published,
                abstract=plain_text(item.get("abstract")),
                discovery_source="semantic_scholar",
                discovery_query=query,
            )
        )
    return records


def pubmed_article_records(xml_text: str, query: str) -> list[PaperRecord]:
    root = ET.fromstring(xml_text)
    records = []
    for article in root.findall(".//PubmedArticle"):
        pmid = plain_text(article.findtext(".//PMID", default=""))
        title = plain_text(article.findtext(".//ArticleTitle", default="")) or "Untitled paper"
        journal = plain_text(article.findtext(".//Journal/Title", default=""))
        year = plain_text(article.findtext(".//PubDate/Year", default=""))
        abstract = " ".join(plain_text(node.text) for node in article.findall(".//AbstractText") if node.text)
        authors = []
        for author in article.findall(".//Author"):
            name = " ".join(
                part
                for part in [
                    plain_text(author.findtext("ForeName", default="")),
                    plain_text(author.findtext("LastName", default="")),
                ]
                if part
            )
            if name:
                authors.append(name)
        doi = ""
        for article_id in article.findall(".//ArticleId"):
            if article_id.attrib.get("IdType") == "doi":
                doi = plain_text(article_id.text)
                break
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
        records.append(
            PaperRecord(
                paper_id=stable_id(title, doi=doi, url=url),
                title=title,
                authors=authors,
                year=year,
                source="PubMed",
                journal=journal,
                doi=doi,
                pmid=pmid,
                url=url,
                published=year,
                abstract=abstract,
                discovery_source="pubmed",
                discovery_query=query,
            )
        )
    return records


def search_pubmed(query: str, config: dict[str, Any]) -> list[PaperRecord]:
    retmax = int(config.get("max_results_per_source", 25))
    since = query_since_date(config).replace("-", "/")
    params = {
        "db": "pubmed",
        "term": f'({query}) AND ("{since}"[Date - Publication] : "3000"[Date - Publication])',
        "retmode": "json",
        "retmax": str(retmax),
        "sort": "pub date",
    }
    api_key = str(config.get("ncbi_api_key", "")).strip()
    if api_key:
        params["api_key"] = api_key
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urllib.parse.urlencode(params)
    payload = http_json(search_url)
    ids = payload.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []
    fetch_params = {"db": "pubmed", "id": ",".join(ids), "retmode": "xml"}
    if api_key:
        fetch_params["api_key"] = api_key
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + urllib.parse.urlencode(fetch_params)
    return pubmed_article_records(http_text(fetch_url), query)


def record_from_mapping(item: dict[str, Any], source: str = "fixture") -> PaperRecord:
    title = first_present(item, ["title", "name"]) or "Untitled paper"
    authors = []
    for author in as_list(item.get("authors") or item.get("author")):
        if isinstance(author, dict):
            text = first_present(author, ["name", "display_name", "full_name"])
        else:
            text = plain_text(author)
        if text:
            authors.append(text)
    published = first_present(item, ["published", "published_date", "date", "year"])
    doi = first_present(item, ["doi", "DOI"])
    arxiv_id = first_present(item, ["arxiv_id", "arxivId", "arxiv"])
    pmid = first_present(item, ["pmid", "PubMed"])
    url = first_present(item, ["url", "link", "entry_id"])
    return PaperRecord(
        paper_id=first_present(item, ["paper_id"]) or stable_id(title, doi=doi, arxiv_id=arxiv_id, url=url),
        title=title,
        authors=authors,
        year=year_from_date(published),
        source=first_present(item, ["source", "provider"]) or source,
        journal=first_present(item, ["journal", "venue", "publication_venue"]),
        doi=doi,
        arxiv_id=arxiv_id,
        pmid=pmid,
        url=url,
        pdf_url=first_present(item, ["pdf_url", "pdfUrl", "pdf"]),
        published=published,
        abstract=first_present(item, ["abstract", "summary", "abstract_raw"]),
        discovery_source=first_present(item, ["discovery_source"]) or source,
        discovery_query=first_present(item, ["discovery_query"]),
        topics=[str(topic) for topic in as_list(item.get("topics")) if str(topic).strip()],
    )


def load_fixture_records(config: dict[str, Any]) -> list[PaperRecord]:
    fixture_path = str(config.get("fixture_records_path") or config.get("fixture_path") or "").strip()
    if not fixture_path:
        return []
    path = Path(fixture_path).expanduser().resolve()
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(payload, dict):
        raw_records = payload.get("records") or payload.get("papers") or payload.get("items") or []
    elif isinstance(payload, list):
        raw_records = payload
    else:
        raw_records = []
    return [record_from_mapping(item, "fixture") for item in raw_records if isinstance(item, dict)]


def discover_records(config: dict[str, Any]) -> list[PaperRecord]:
    fixture_records = load_fixture_records(config)
    if fixture_records:
        for record in fixture_records:
            if not record.topics:
                record.topics = topic_terms(config)
        return dedupe_records(fixture_records)

    sources = config.get(
        "sources",
        {
            "openalex": True,
            "crossref": True,
            "arxiv": True,
            "semantic_scholar": False,
            "pubmed": False,
        },
    )
    queries = [str(item).strip() for item in config.get("queries", []) if str(item).strip()]
    if not queries:
        queries = topic_terms(config)
    match_venue = venue_matcher(config)
    require_venue_match = bool(config.get("require_venue_match", False))
    all_records: list[PaperRecord] = []
    searchers = [
        ("openalex", search_openalex),
        ("crossref", search_crossref),
        ("arxiv", search_arxiv),
        ("semantic_scholar", search_semantic_scholar),
        ("pubmed", search_pubmed),
    ]
    for query in queries:
        for source_name, searcher in searchers:
            if sources and not sources.get(source_name, False):
                continue
            try:
                records = searcher(query, config)
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ET.ParseError) as exc:
                print(f"[warn] {source_name} failed for query '{query}': {exc}", file=sys.stderr)
                continue
            for record in records:
                record.venue_match = match_venue(record.journal)
                record.topics = topic_terms(config)
                if require_venue_match and record.journal != "arXiv" and not record.venue_match:
                    continue
                all_records.append(record)
            time.sleep(float(config.get("request_delay_seconds", 0.3)))
    return dedupe_records(all_records)


def dedupe_records(records: list[PaperRecord]) -> list[PaperRecord]:
    seen: dict[str, PaperRecord] = {}
    for record in records:
        key = record.dedupe_key()
        existing = seen.get(key)
        if not existing:
            seen[key] = record
            continue
        if not existing.pdf_url and record.pdf_url:
            existing.pdf_url = record.pdf_url
        if not existing.abstract and record.abstract:
            existing.abstract = record.abstract
        if not existing.journal and record.journal:
            existing.journal = record.journal
        if record.venue_match:
            existing.venue_match = True
    return list(seen.values())


def is_probably_pdf_url(url: str) -> bool:
    lower = url.lower()
    return lower.startswith(("http://", "https://")) and (".pdf" in lower or "/pdf/" in lower)


def download_pdf(record: PaperRecord, pdf_dir: Path, timeout: int = 45) -> bool:
    if not record.pdf_url or not is_probably_pdf_url(record.pdf_url):
        return False
    pdf_dir.mkdir(parents=True, exist_ok=True)
    output = pdf_dir / f"{record.paper_id}.pdf"
    if output.exists() and output.stat().st_size > 0:
        record.pdf_path = str(output)
        return True
    req = urllib.request.Request(record.pdf_url, headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content_type = response.headers.get("Content-Type", "")
            content = response.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"[warn] PDF download failed for {record.paper_id}: {exc}", file=sys.stderr)
        return False
    if b"%PDF" not in content[:1024] and "pdf" not in content_type.lower():
        print(f"[warn] skipped non-PDF response for {record.paper_id}: {content_type}", file=sys.stderr)
        return False
    output.write_bytes(content)
    record.pdf_path = str(output)
    return True


def yaml_list(values: list[str]) -> str:
    if not values:
        return "[]"
    return "[" + ", ".join(json.dumps(str(item), ensure_ascii=False) for item in values) + "]"


def yaml_value(value: str) -> str:
    return json.dumps(value or "", ensure_ascii=False)


def paper_markdown(record: PaperRecord, added: str, evidence_status: str) -> str:
    if evidence_status not in VALID_EVIDENCE:
        evidence_status = "metadata-only"
    pdf_path_line = f"- Local PDF: {record.pdf_path}" if record.pdf_path else "- Local PDF:"
    venue_status = "allowlist-match" if record.venue_match else "not matched or not configured"
    return f"""---
type: paper
paper_id: {yaml_value(record.paper_id)}
title: {yaml_value(record.title)}
authors: {yaml_list(record.authors)}
year: {yaml_value(record.year)}
source: {yaml_value(record.source)}
journal: {yaml_value(record.journal)}
doi: {yaml_value(record.doi)}
arxiv_id: {yaml_value(record.arxiv_id)}
pmid: {yaml_value(record.pmid)}
url: {yaml_value(record.url)}
pdf_url: {yaml_value(record.pdf_url)}
pdf_path: {yaml_value(record.pdf_path)}
zotero_key: ""
zotero_status: pending
evidence_status: {evidence_status}
topics: {yaml_list(record.topics)}
roles: [candidate]
added: {yaml_value(added)}
last_reviewed: ""
discovery_source: {yaml_value(record.discovery_source)}
discovery_query: {yaml_value(record.discovery_query)}
venue_status: {yaml_value(venue_status)}
---

# {record.title}

## Status

- Evidence status: {evidence_status}
- Zotero: pending
- Venue filter: {venue_status}
- Next action: screen the abstract, verify access rights, then import accepted items into Zotero.

## Abstract Summary

{record.abstract}

## Why It Matters

## Methods

## Evidence Extracted

## Limitations

## Links

- Source: {record.url}
- PDF: {record.pdf_url}
- DOI: {record.doi}
{pdf_path_line}

## Review Use

- Can support: candidate discovery and search-log coverage.
- Cannot support yet: paper-level claims until the full text is read and the evidence status is updated.
"""


def daily_markdown(records: list[PaperRecord], run_date: str, config: dict[str, Any]) -> str:
    lines = [
        f"# Daily Literature Update - {run_date}",
        "",
        f"- Topic: {config.get('topic', '')}",
        f"- New records: {len(records)}",
        f"- Query window start: {query_since_date(config)}",
        "",
        "## New Papers",
        "",
    ]
    for record in records:
        venue = f" - {record.journal}" if record.journal else ""
        lines.append(f"- [[papers/{record.paper_id}|{record.title}]]{venue}")
    lines.extend(
        [
            "",
            "## Triage",
            "",
            "- Import to Zotero:",
            "- Read full text:",
            "- Exclude:",
            "",
            "## Evidence Boundary",
            "",
            "These records are discovery outputs. They must not support detailed literature-review claims until evidence_status is upgraded after full-text reading.",
            "",
        ]
    )
    return "\n".join(lines)


def update_seen(root: Path, records: list[PaperRecord], run_date: str) -> list[PaperRecord]:
    seen_path = root / "data" / "seen_papers.json"
    seen = load_json(seen_path) if seen_path.exists() else {}
    new_records = []
    for record in records:
        key = record.dedupe_key()
        if key not in seen:
            new_records.append(record)
        seen[key] = {
            "paper_id": record.paper_id,
            "title": record.title,
            "first_seen": seen.get(key, {}).get("first_seen", run_date),
            "last_seen": run_date,
            "source": record.discovery_source,
            "journal": record.journal,
            "doi": record.doi,
            "arxiv_id": record.arxiv_id,
            "pmid": record.pmid,
        }
    write_json(seen_path, seen)
    return new_records


def ensure_layout(root: Path) -> None:
    for dirname in ["config", "daily", "papers", "data", "pdfs", "topics", "claims", "reviews", "templates"]:
        (root / dirname).mkdir(parents=True, exist_ok=True)
    working_review = root / "reviews" / "working-review.md"
    if not working_review.exists():
        working_review.write_text("# Working Review\n\n## Current Synthesis\n\n## Evidence Boundary\n", encoding="utf-8")


def run_pipeline(config_path: Path, dry_run: bool = False) -> dict[str, Any]:
    config = load_json(config_path)
    root = Path(config.get("wiki_root") or config.get("vault") or "Literature").expanduser().resolve()
    run_date = str(config.get("run_date") or date.today().isoformat())
    ensure_layout(root)
    vault_config_path = root / "config" / "literature-review-config.json"
    if not vault_config_path.exists():
        write_json(vault_config_path, config)

    records = discover_records(config)
    raw_path = root / "data" / "discovery" / f"{run_date}.json"
    write_json(raw_path, [record.as_dict() for record in records])

    if dry_run:
        return {
            "wiki_root": str(root),
            "discovered": len(records),
            "new_records": 0,
            "downloaded_pdfs": 0,
            "raw_path": str(raw_path),
            "dry_run": True,
        }

    pdf_dir = root / str(config.get("pdf_dir", "pdfs"))
    downloaded = 0
    if config.get("download_open_access_pdfs", True):
        for record in records:
            if download_pdf(record, pdf_dir):
                downloaded += 1

    new_records = update_seen(root, records, run_date)
    evidence_status = str(config.get("new_record_evidence_status", "metadata-only"))
    for record in new_records:
        note_path = root / "papers" / f"{record.paper_id}.md"
        if note_path.exists() and not config.get("overwrite_paper_notes", False):
            continue
        note_path.write_text(paper_markdown(record, run_date, evidence_status), encoding="utf-8")

    daily_path = root / "daily" / f"{run_date}.md"
    daily_path.write_text(daily_markdown(new_records, run_date, config), encoding="utf-8")

    return {
        "wiki_root": str(root),
        "discovered": len(records),
        "new_records": len(new_records),
        "downloaded_pdfs": downloaded,
        "raw_path": str(raw_path),
        "daily_path": str(daily_path),
        "dry_run": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover papers, download authorized OA PDFs, and update an Obsidian literature wiki.")
    parser.add_argument("--config", required=True, help="Path to literature monitor JSON config.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and write raw discovery JSON without updating paper notes.")
    args = parser.parse_args()
    summary = run_pipeline(Path(args.config).resolve(), dry_run=args.dry_run)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
