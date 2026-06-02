# Obsidian Schema

## Folder Layout

```text
Literature/
  dashboard.md
  config/
    literature-review-config.json
  daily/
  papers/
  topics/
  claims/
  reviews/
  templates/
  data/
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
zotero_key: ""
zotero_status: pending
evidence_status: metadata-only
topics: []
roles: []
added: ""
last_reviewed: ""
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
