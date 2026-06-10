# Obsidian Schema

## Folder Layout

```text
Literature/
  dashboard.md
  config/
    literature-review-config.json
  daily/
  papers/
  pdfs/
  topics/
  claims/
  reviews/
  templates/
  data/
    discovery/
    corpus/
```

## Paper Note Frontmatter

```yaml
---
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
pdf_path: ""
zotero_key: ""
zotero_status: pending
evidence_status: metadata-only
topics: []
roles: []
added: ""
last_reviewed: ""
discovery_source: ""
discovery_query: ""
venue_status: ""
---
```

## Paper Note Sections

```markdown
# Paper Title

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
```

## Topic Page Sections

```markdown
# Topic Name

## Scope

## Taxonomy

## Foundational Papers

## Methods

## Applications

## Contradictions

## Candidate Papers

## Open Questions
```

## Claim Page Sections

```markdown
# Claim

## Claim Text

## Supporting Evidence

## Contradictory Evidence

## Evidence Boundary

## Review Wording
```

## Review Files

Use these defaults:

- `reviews/working-review.md`: current synthesis prose
- `reviews/gaps.md`: research gaps and uncertainties
- `reviews/search-log.md`: search strings, sources, dates, and counts
- `reviews/screening-log.md`: inclusion/exclusion decisions

## Data Files

- `data/seen_papers.json`: dedupe state keyed by DOI, arXiv ID, or normalized title.
- `data/discovery/YYYY-MM-DD.json`: raw daily discovery records.
- `data/corpus/sentences.jsonl`: sentence-level writing corpus for MCP use.
- `data/corpus/phrase-patterns.md`: recurring phrase starts grouped by rhetorical function.
- `pdfs/<paper_id>.pdf`: optional authorized open-access PDFs.
