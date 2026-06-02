# Literature Review Wiki Skill

Codex skill for building an evidence-first literature review workflow that combines scholarly paper discovery, Zotero-backed bibliography management, daily paper monitoring, and an Obsidian wiki.

## What It Does

- Discovers papers across metadata and preprint sources such as OpenAlex, Semantic Scholar, Crossref, arXiv, PubMed, and MCP-based paper search tools.
- Treats Zotero as the bibliographic source of truth.
- Treats Obsidian as the synthesis layer for paper notes, topic pages, claim maps, daily updates, and working review drafts.
- Integrates daily radar feeds such as `lelouchsola/arXiv-Daily-Summarizer` by converting `site/latest.json` into local Obsidian notes.
- Preserves evidence boundaries so metadata-only candidates are not silently promoted into review-ready claims.

## 中文说明

这个仓库不是一个独立运行的 Web 应用，而是一个给 Codex 使用的 `literature-review-wiki` skill。它的作用是把“找论文、筛论文、入库、写综述、维护 Obsidian wiki、每日追踪新论文”组织成一套可重复执行的工作流。

它默认把 Zotero 作为文献库的元数据来源，把 Obsidian 作为知识整理和综述写作层。Codex 在使用这个 skill 时，会先区分论文处于什么证据状态，例如只是检索到元数据、已经读过摘要、还是已经读过全文。这样可以避免把“候选论文”直接写成综述结论。

## 能实现什么效果

使用这个 skill 后，可以形成以下效果：

1. 按某个研究主题初始化一个 Obsidian 文献综述目录，包括 `papers/`、`topics/`、`claims/`、`reviews/`、`daily/` 等页面结构。
2. 把 `lelouchsola/arXiv-Daily-Summarizer` 生成的 `site/latest.json` 转换成 Obsidian 每日更新记录和单篇论文笔记。
3. 把新论文按主题、方法、应用、证据状态和综述用途进行分类，而不是只保存一张论文列表。
4. 维护一个持续更新的 literature review：新论文先进入候选池，经过摘要筛选或全文阅读后，再进入主题页、论点页和综述草稿。
5. 保留 license 和证据边界：只默认使用开放获取或用户有权访问的 PDF；参考第三方仓库时只做链接和互操作说明，不复制不兼容 license 的代码。

最终目标是得到一个本地可持续维护的研究 wiki：Zotero 管文献条目，Obsidian 管知识结构，Codex 负责按流程检索、整理、更新和检查证据边界。

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
