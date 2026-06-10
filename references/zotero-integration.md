# Zotero Integration Boundary

Zotero should remain the bibliographic source of truth when available. This project can create Obsidian paper stubs before Zotero import, but it must not fabricate Zotero keys or imply that a paper was imported when it was not.

## Fields to Preserve

Paper notes should preserve these fields for later Zotero reconciliation:

- `doi`
- `arxiv_id`
- `pmid`
- `url`
- `pdf_url`
- `pdf_path`
- `zotero_key`
- `zotero_status`

Use `zotero_status: pending` until the item is actually present in Zotero.

## Recommended Import Path

1. Discover papers with `litwiki-discover`.
2. Screen candidates in Obsidian.
3. Import accepted papers to Zotero by DOI, arXiv ID, PMID, or official URL.
4. Attach only authorized PDFs.
5. Export or sync the Zotero citation key back into the paper note.
6. Upgrade `zotero_status` only after the Zotero item is confirmed.

## Optional MCP/Better BibTeX Path

If a Zotero MCP server or Better BibTeX export is available, add a separate reconciliation script rather than mixing Zotero writes into discovery. The reconciliation script should:

- read Obsidian paper notes;
- match by DOI, arXiv ID, PMID, or title;
- update `zotero_key` and `zotero_status`;
- never overwrite manually curated evidence sections;
- log unmatched or ambiguous items.

## Evidence Boundary

Zotero import is bibliographic confirmation, not full-text review. A paper can be `zotero_status: imported` while still being `evidence_status: metadata-only` or `abstract-screened`.
