# Tool Stack

## Recommended Composition

No single GitHub repository is currently a complete mature solution for multi-source discovery, compliant PDF ingestion, Zotero, daily monitoring, and Obsidian literature-review wiki maintenance. Use a composed stack.

## Search and Download

- `openags/paper-search-mcp`: multi-source search and open/public paper download. Best fit for agent-driven search workflows.
- `dsebastien/ai-skill-scholar`: OpenAlex-based search, citation graph, and two-pass review orchestration. Useful when API keys are unavailable.
- `Zikt/scholare`: config-driven literature search and Markdown note generation. Useful as a lightweight reference.
- `CarinaSchoppe/PISMA-Literature-Review-Pipeline-Automation-Tool`: systematic-review style search, dedupe, citation expansion, and report generation.

## Daily Monitoring

- `lelouchsola/arXiv-Daily-Summarizer`: GitHub Actions daily static site. Current README says it fetches daily papers/articles, scores relevance/source quality, generates Chinese summaries/comments, writes `site/latest.json` and `site/index.html`, and deploys to GitHub Pages. It is useful as a radar feed but does not retain cross-day history.
- `TideDra/zotero-arxiv-daily`: recommends new arXiv papers based on an existing Zotero library.
- `ziwenhahaha/daily-paper-reader`: GitHub Actions and GitHub Pages pattern for daily arXiv/OpenReview paper reading.
- `theislab/paperbee`: daily scientific paper discovery and messaging channels.

## Zotero

- `Xevos117/mcp-zotero`: MCP server for Zotero search, organization, add-by-DOI, PDF import, full-text indexing, and citation workflows.
- `retorquere/zotero-better-bibtex`: stable citation keys and BibTeX export.
- `windingwind/zotero-better-notes`: Zotero-side note management.

## Obsidian

- `obsidian-community/obsidian-zotero-integration`: import citations, bibliographies, Zotero notes, and PDF annotations into Obsidian.
- `chauff/paper-note-filler`: Obsidian plugin for notes from arXiv, ACL Anthology, and Semantic Scholar.
- `XuanjinZhu/zotero-obsidian-wiki-bridge`: local-first paper processing and vault maintenance reference.
- `Geek96/paper-research-skill`: closest skill-structure reference for `search/download -> Zotero -> Obsidian wiki`.

## Recommended Skill Behavior

Use GitHub projects as components, not as hidden dependencies. When a component is unavailable, fall back to direct APIs or user-provided exports. Always write down which source produced each candidate paper.
