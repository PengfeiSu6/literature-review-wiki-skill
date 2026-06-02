# Literature Review Wiki Skill

Codex skill for building an evidence-first literature review workflow that combines scholarly paper discovery, Zotero-backed bibliography management, daily paper monitoring, and an Obsidian wiki.

## What It Does

- Discovers papers across metadata and preprint sources such as OpenAlex, Semantic Scholar, Crossref, arXiv, PubMed, and MCP-based paper search tools.
- Treats Zotero as the bibliographic source of truth.
- Treats Obsidian as the synthesis layer for paper notes, topic pages, claim maps, daily updates, and working review drafts.
- Integrates daily radar feeds such as `lelouchsola/arXiv-Daily-Summarizer` by converting `site/latest.json` into local Obsidian notes.
- Preserves evidence boundaries so metadata-only candidates are not silently promoted into review-ready claims.

## Repository Contents

```text
SKILL.md
agents/openai.yaml
LICENSE
references/
  license-compliance.md
  automation.md
  evidence-policy.md
  obsidian-schema.md
  tool-stack.md
  workflow.md
scripts/
  init_lit_review_project.py
  daily_json_to_obsidian.py
  lint_lit_review_wiki.py
```

## Install

Copy or clone this folder into your Codex skills directory:

```powershell
Copy-Item -Recurse . "$env:USERPROFILE\.codex\skills\literature-review-wiki"
```

Then start a new Codex session and invoke:

```text
Use $literature-review-wiki to set up a literature review wiki for <topic>.
```

## Quick Start

Create an Obsidian literature review wiki:

```powershell
python .\scripts\init_lit_review_project.py `
  --root "C:\path\to\ObsidianVault\Literature" `
  --topic "industrial energy flexibility" `
  --zotero-collection "industrial energy flexibility"
```

Convert a daily paper feed, such as `site/latest.json` from `lelouchsola/arXiv-Daily-Summarizer`, into Obsidian notes:

```powershell
python .\scripts\daily_json_to_obsidian.py `
  --input "C:\path\to\latest.json" `
  --vault "C:\path\to\ObsidianVault\Literature" `
  --source-name "arXiv-Daily-Summarizer"
```

Check the wiki structure and evidence boundaries:

```powershell
python .\scripts\lint_lit_review_wiki.py `
  --vault "C:\path\to\ObsidianVault\Literature"
```

## Recommended Tool Stack

- Search/download: `openags/paper-search-mcp`, OpenAlex, Semantic Scholar, Crossref, arXiv, PubMed.
- Daily feed: `lelouchsola/arXiv-Daily-Summarizer`, `TideDra/zotero-arxiv-daily`, or topic-specific RSS.
- Zotero: `Xevos117/mcp-zotero`, Better BibTeX, Zotero Better Notes.
- Obsidian: Obsidian Zotero Integration and the wiki schema in `references/obsidian-schema.md`.

## Reference Licenses

This repository is released under the MIT License. It does not copy, vendor, embed, or redistribute code from the referenced GitHub projects.

See [references/license-compliance.md](references/license-compliance.md) for the referenced repositories, their detected SPDX licenses, and the allowed usage boundary. In short: MIT projects are permissive with attribution; GPL/AGPL projects are reference or separate-tool integrations unless their license obligations are satisfied; no-license or `NOASSERTION` projects must not be copied without manual review or permission.

## Evidence Policy

The skill distinguishes:

- `metadata-only`
- `abstract-screened`
- `fulltext-read`
- `citation-chain`
- `excluded`

Only `fulltext-read` papers should support detailed literature-review claims. The default workflow uses only authorized open-access PDFs or user-provided files with confirmed access rights.

## Suggested GitHub Description

```text
Codex skill for Zotero-backed literature reviews, daily paper monitoring, and Obsidian wiki maintenance.
```
