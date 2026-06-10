---
name: literature-review-wiki
description: Use when discovering, screening, downloading open-access scholarly papers for a topic; importing or reconciling papers with Zotero; creating or updating an Obsidian literature-review wiki; maintaining daily paper-monitoring feeds such as arXiv-Daily-Summarizer; or incrementally revising a literature review from newly found papers.
---

# Literature Review Wiki

## Core Rule

Treat Zotero as the bibliographic source of truth, Obsidian as the synthesis and wiki layer, and the literature review as an evidence-bound living document. Do not invent findings, do not imply a paper was read if only metadata was screened, and do not download copyrighted PDFs from unauthorized sources.

## Decision Tree

1. If the user asks to start a new topic, create a project config and Obsidian skeleton with `scripts/init_lit_review_project.py`.
2. If the user provides daily paper JSON, a GitHub Pages `latest.json`, or output from `lelouchsola/arXiv-Daily-Summarizer`, convert it into daily notes and paper stubs with `scripts/daily_json_to_obsidian.py`.
3. If the user asks for recurring topic or high-journal discovery, create a monitor config from `examples/literature-config.example.json` and run `scripts/literature_pipeline.py`.
4. If the user asks for search, combine broad discovery sources:
   - OpenAlex for cross-field metadata and citation graph seed expansion.
   - Semantic Scholar, Crossref, PubMed, arXiv, bioRxiv/medRxiv where relevant.
   - `openags/paper-search-mcp` when available for multi-source search/download.
   - `lelouchsola/arXiv-Daily-Summarizer` when a daily arXiv/RSS-style paper radar or GitHub Pages digest is useful.
5. If the user asks to build a writing corpus or writing MCP, run `scripts/build_corpus.py` and configure `scripts/literature_mcp_server.py`.
6. If the user asks to import papers, prefer Zotero/MCP/Zotero API workflows. Store DOI, arXiv ID, URL, OA PDF status, and citation key before writing synthesis notes.
7. If the user asks to update the review, first inspect new notes and evidence status; then update topic pages, claim pages, and review drafts separately.
8. Before calling the wiki current, run `scripts/lint_lit_review_wiki.py` or perform the same checks manually.

## Required Evidence Boundaries

- `metadata-only`: title/abstract/source metadata screened, no full text read.
- `abstract-screened`: abstract read and categorized, no full-text claims.
- `fulltext-read`: paper text or OA PDF read sufficiently to support claims.
- `citation-chain`: added because it is cited by or cites a seed paper; still needs screening.
- `excluded`: screened out with a short reason.

Only `fulltext-read` papers can support detailed literature-review claims. Lower statuses can support discovery logs, candidate lists, and gap hypotheses, but must be labeled as such.

## Obsidian Wiki Layout

Use this default vault-side layout unless the user has an existing convention:

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

Paper notes should use stable identifiers from DOI, arXiv ID, PMID, or a title hash. Topic pages should link papers by role, not just list them:

- `foundational`
- `method`
- `dataset`
- `benchmark`
- `application`
- `survey`
- `contradictory`
- `candidate`

## Daily Monitoring

For recurring checks, use the platform automation tool when available. In Codex Desktop, search for `automation_update` first if the user wants a reminder or recurring job. If no automation tool is available, provide a GitHub Actions or Windows Task Scheduler fallback.

For the built-in daily pipeline:

1. Copy `examples/literature-config.example.json` and set `topic`, `queries`, `included_venues`, and `wiki_root`.
2. Run `python scripts/literature_pipeline.py --config <config.json>`.
3. Run `python scripts/build_corpus.py --vault <wiki_root>`.
4. Run `python scripts/lint_lit_review_wiki.py --vault <wiki_root> --require-corpus` before exposing the MCP.
5. Use `scripts/literature_mcp_server.py --vault <wiki_root>` from the writing agent's MCP configuration.

For `lelouchsola/arXiv-Daily-Summarizer`, use its static-site output as a radar feed:

1. Run or fetch its daily `site/latest.json`.
2. Convert new records into Obsidian notes with `scripts/daily_json_to_obsidian.py`.
3. Add promising papers to Zotero by DOI/arXiv ID/PDF through Zotero tooling.
4. Update `daily/`, `papers/`, `topics/`, `claims/`, and `reviews/` incrementally.

Do not rely on the upstream repository for history retention; keep local history in the Obsidian `data/seen_papers.json` file or Zotero collections.

## References

Load only the reference needed for the current task:

- `references/workflow.md`: end-to-end workflow from search to review update.
- `references/tool-stack.md`: recommended GitHub/tool stack and how each component fits.
- `references/license-compliance.md`: reference repositories, detected licenses, and reuse boundaries.
- `references/obsidian-schema.md`: folder structure, note schema, and templates.
- `references/automation.md`: daily monitoring with GitHub Actions, Codex automation, or local schedulers.
- `references/evidence-policy.md`: source legality, evidence statuses, and review-claim rules.
- `references/zotero-integration.md`: Zotero reconciliation fields, import boundaries, and citation-key guardrails.

## Scripts

- `scripts/init_lit_review_project.py`: create config, folders, and starter Obsidian pages.
- `scripts/literature_pipeline.py`: discover topic papers, filter configured venues, download authorized OA PDFs, and update Obsidian.
- `scripts/daily_json_to_obsidian.py`: convert daily JSON feeds into daily notes and paper stubs.
- `scripts/build_corpus.py`: build `data/corpus/sentences.jsonl` and phrase-pattern notes from paper notes/PDFs.
- `scripts/literature_mcp_server.py`: serve the corpus as MCP tools for writing assistance.
- `scripts/lint_lit_review_wiki.py`: check config, duplicate paper IDs, missing source links, evidence-status issues, and optional MCP corpus readiness.

Run scripts with `python` and inspect outputs before changing user-owned notes.
