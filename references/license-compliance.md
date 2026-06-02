# Reference Repositories and License Compatibility

This repository contains original skill instructions and helper scripts. It does not copy, vendor, embed, or redistribute source code from the reference repositories below.

License data was checked from GitHub repository metadata on 2026-06-02. Re-check upstream licenses before copying code, vendoring files, or redistributing modified versions.

## Compatibility Rule

- MIT and other permissive licenses: can usually be reused if copyright and license notices are preserved.
- GPL-3.0: do not copy or combine code into this MIT repository unless the resulting distribution follows GPL-3.0.
- AGPL-3.0: do not copy, vendor, or run as a network service component without following AGPL-3.0 obligations.
- Other/NOASSERTION or no license file: treat as not reusable for code copying until the license is manually reviewed or permission is obtained.
- Links, factual descriptions, and interoperability notes are reference use only and do not import third-party license obligations into this repository.

## Referenced Projects

| Repository | Role in this skill | Detected license | Compatibility note |
| --- | --- | --- | --- |
| [openags/paper-search-mcp](https://github.com/openags/paper-search-mcp) | Multi-source paper search/download reference | MIT | Permissive; preserve notices if code is reused. |
| [dsebastien/ai-skill-scholar](https://github.com/dsebastien/ai-skill-scholar) | OpenAlex search and review-skill reference | MIT | Permissive; preserve notices if code is reused. |
| [Zikt/scholare](https://github.com/Zikt/scholare) | Config-driven literature pipeline reference | MIT | Permissive; preserve notices if code is reused. |
| [CarinaSchoppe/PISMA-Literature-Review-Pipeline-Automation-Tool](https://github.com/CarinaSchoppe/PISMA-Literature-Review-Pipeline-Automation-Tool) | PRISMA/systematic-review workflow reference | GPL-3.0 | Reference only here; do not copy code into this MIT repo without GPL compliance. |
| [lelouchsola/arXiv-Daily-Summarizer](https://github.com/lelouchsola/arXiv-Daily-Summarizer) | Daily paper radar and `latest.json` feed reference | MIT | Permissive; preserve notices if code is reused. |
| [TideDra/zotero-arxiv-daily](https://github.com/TideDra/zotero-arxiv-daily) | Zotero-based daily arXiv recommendation reference | AGPL-3.0 | Reference or separate-tool use only unless AGPL obligations are satisfied. |
| [ziwenhahaha/daily-paper-reader](https://github.com/ziwenhahaha/daily-paper-reader) | GitHub Actions and Pages daily-reader reference | MIT | Permissive; preserve notices if code is reused. |
| [theislab/paperbee](https://github.com/theislab/paperbee) | Daily scientific paper discovery reference | MIT | Permissive; preserve notices if code is reused. |
| [Xevos117/mcp-zotero](https://github.com/Xevos117/mcp-zotero) | Zotero MCP workflow reference | Other/NOASSERTION | Reference only until license terms are manually reviewed. |
| [retorquere/zotero-better-bibtex](https://github.com/retorquere/zotero-better-bibtex) | Zotero citation-key tooling reference | MIT | Permissive; preserve notices if code is reused. |
| [windingwind/zotero-better-notes](https://github.com/windingwind/zotero-better-notes) | Zotero note-management reference | AGPL-3.0 | Reference or separate-tool use only unless AGPL obligations are satisfied. |
| [obsidian-community/obsidian-zotero-integration](https://github.com/obsidian-community/obsidian-zotero-integration) | Obsidian/Zotero import workflow reference | GPL-3.0 | Reference or separate plugin use only; do not copy code into this MIT repo without GPL compliance. |
| [chauff/paper-note-filler](https://github.com/chauff/paper-note-filler) | Obsidian paper-note generation reference | No license file detected | Reference only; do not copy code without permission. |
| [XuanjinZhu/zotero-obsidian-wiki-bridge](https://github.com/XuanjinZhu/zotero-obsidian-wiki-bridge) | Zotero-Obsidian wiki bridge reference | MIT | Permissive; preserve notices if code is reused. |
| [Geek96/paper-research-skill](https://github.com/Geek96/paper-research-skill) | Similar skill-structure reference | MIT | Permissive; preserve notices if code is reused. |

## Practical Use Policy

The current repository may link to, interoperate with, or recommend installing third-party projects as separate tools. It should not vendor GPL/AGPL/no-license code into `scripts/`, `references/`, or `assets/`. If future work copies implementation code from any upstream project, add the upstream license text and attribution, and revisit this repository's licensing.
