# Literature Review Wiki Skill

Codex skill and local toolkit for building an evidence-first literature review workflow: discover papers, download authorized open-access PDFs, maintain an Obsidian literature wiki, build a sentence-level writing corpus, and expose that corpus through MCP for academic writing assistance.

## What It Does

- Discovers papers from OpenAlex, Crossref, and arXiv with topic queries, venue allowlists, and daily lookback windows.
- Downloads only authorized open-access PDFs when a public PDF URL is available.
- Maintains an Obsidian wiki with paper notes, daily updates, topic pages, claim pages, and review drafts.
- Keeps `metadata-only`, `abstract-screened`, `fulltext-read`, `citation-chain`, and `excluded` evidence states explicit.
- Builds a local writing corpus from paper notes and optional local PDFs.
- Serves the corpus as an MCP server for sentence examples, phrase patterns, paper context, and wording-risk checks.

## 中文说明

这个项目面向“持续文献库 + 论文写作辅助”的工作流。它不是付费数据库替代品，也不会绕过出版社权限；它负责把公开可发现、合法可下载或用户有权访问的论文材料整理到本地 Obsidian 中，并把这些材料转成可被写作代理调用的语料库。

核心原则是证据边界：只检索到元数据的论文只能标记为 `metadata-only`；读过摘要后可以标记为 `abstract-screened`；只有真正读过全文并提取证据后，才应标记为 `fulltext-read` 并用于综述结论。

## Repository Contents

```text
SKILL.md
PROJECT_INTRODUCTION.md
PROMPT_FOR_MULTICA.md
requirements.txt
agents/
references/
examples/
  literature-config.example.json
  mcp-server-config.example.json
  run_daily_literature_update.ps1
  github-actions-daily-literature-update.yml
scripts/
  init_lit_review_project.py
  literature_pipeline.py
  daily_json_to_obsidian.py
  build_corpus.py
  literature_mcp_server.py
  lint_lit_review_wiki.py
```

## Install

Copy or clone this folder into your Codex skills directory:

```powershell
Copy-Item -Recurse . "$env:USERPROFILE\.codex\skills\literature-review-wiki"
```

Install optional runtime dependencies for MCP and PDF extraction:

```powershell
python -m pip install -r requirements.txt
```

For editable development with CLI entry points:

```powershell
python -m pip install -e ".[dev]"
```

## Quick Start

Create an Obsidian literature review wiki:

```powershell
python .\scripts\init_lit_review_project.py `
  --root "C:\path\to\ObsidianVault\Literature\industrial-energy-flexibility" `
  --topic "industrial energy flexibility" `
  --zotero-collection "industrial energy flexibility"
```

Copy and edit the monitor config:

```powershell
Copy-Item .\examples\literature-config.example.json .\work\my-literature-config.json
```

Run discovery, OA PDF download, and Obsidian update:

```powershell
python .\scripts\literature_pipeline.py --config .\work\my-literature-config.json
```

Equivalent installed CLI:

```powershell
litwiki-discover --config .\work\my-literature-config.json
```

Build the writing corpus:

```powershell
python .\scripts\build_corpus.py `
  --vault "C:\path\to\ObsidianVault\Literature\industrial-energy-flexibility"
```

Start the MCP server:

```powershell
python .\scripts\literature_mcp_server.py `
  --vault "C:\path\to\ObsidianVault\Literature\industrial-energy-flexibility"
```

Equivalent installed CLI:

```powershell
litwiki-mcp --vault "C:\path\to\ObsidianVault\Literature\industrial-energy-flexibility"
```

For MCP client configuration, adapt `examples/mcp-server-config.example.json`.

Check the wiki structure and evidence boundaries:

```powershell
python .\scripts\lint_lit_review_wiki.py `
  --vault "C:\path\to\ObsidianVault\Literature\industrial-energy-flexibility"
```

Before exposing the project through MCP, require corpus validation:

```powershell
litwiki-lint `
  --vault "C:\path\to\ObsidianVault\Literature\industrial-energy-flexibility" `
  --require-corpus
```

## Daily Update

For Windows Task Scheduler, use the wrapper in `examples/run_daily_literature_update.ps1`:

```powershell
powershell -ExecutionPolicy Bypass -File .\examples\run_daily_literature_update.ps1 `
  -RepoRoot "C:\path\to\literature-review-wiki-skill" `
  -ConfigPath "C:\path\to\my-literature-config.json"
```

For GitHub Actions, copy `examples/github-actions-daily-literature-update.yml` into `.github/workflows/` and replace the example vault/config paths with a repository-safe setup. Do not commit private PDFs or private Obsidian notes to a public repository.

## Offline Testing

The pipeline supports fixture-driven runs for CI and development:

```json
{
  "topic": "industrial energy flexibility",
  "wiki_root": "work/test-vault",
  "fixture_records_path": "tests/fixtures/discovery-records.json",
  "download_open_access_pdfs": false
}
```

Run tests:

```powershell
python -m pytest -q
```

CI uses the same offline fixture strategy and does not query live scholarly APIs.

## MCP Tools

`scripts/literature_mcp_server.py` exposes:

- `search_literature_corpus`: search sentence examples by keyword, topic, journal, or phrase.
- `suggest_academic_phrases`: return examples for background, gap, method, result, limitation, or general academic functions.
- `get_paper_context`: return the Obsidian paper note for a `paper_id`.
- `check_sentence_against_corpus`: compare a draft sentence with corpus examples and flag unsupported wording such as "prove", "state of the art", or "comprehensive".
- `get_evidence_boundary`: explain how each evidence status may be used in writing.

MCP results are for writing style and traceable context. They must not be used as factual evidence unless the linked paper note is `fulltext-read`.

## Evidence Policy

The skill distinguishes:

- `metadata-only`: search result or metadata only.
- `abstract-screened`: abstract reviewed, no full-text claims.
- `fulltext-read`: full text reviewed sufficiently to support claims.
- `citation-chain`: found through references/citations; still needs screening.
- `excluded`: screened out with a short reason.

Only `fulltext-read` papers should support detailed literature-review claims. The default workflow uses only authorized open-access PDFs or user-provided files with confirmed access rights.

## Recommended Tool Stack

- Search/download: OpenAlex, Crossref, arXiv, optional Semantic Scholar/PubMed metadata, optional `openags/paper-search-mcp`.
- Daily feed: this repository's `literature_pipeline.py`, `lelouchsola/arXiv-Daily-Summarizer`, or topic-specific RSS.
- Zotero: `Xevos117/mcp-zotero`, Better BibTeX, Zotero Better Notes.
- Obsidian: Obsidian Zotero Integration and the wiki schema in `references/obsidian-schema.md`.
- MCP: Python `mcp` SDK with `scripts/literature_mcp_server.py`.

Zotero reconciliation boundaries are documented in `references/zotero-integration.md`.

## Reference Licenses

This repository is released under the MIT License. It does not copy, vendor, embed, or redistribute code from the referenced GitHub projects.

See [references/license-compliance.md](references/license-compliance.md) for referenced repositories, detected SPDX licenses, and allowed usage boundaries.
