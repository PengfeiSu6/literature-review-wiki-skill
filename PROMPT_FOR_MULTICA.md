# Prompt for Multica：完善 Literature Review Wiki Skill 项目

你是 Multica 软件工程代理。请在仓库 `PengfeiSu6/literature-review-wiki-skill` 中继续完善一个面向科研写作的文献库与 MCP 项目。请先审计现有代码，再按优先级实施，不要跳过验证。

## 背景

该项目是一个 Codex skill，目标是把领域内高水平期刊和相关 topic 下的论文持续抓取到本地 Obsidian 文献库中，并基于论文摘要、笔记和开放获取全文建立写作语料库，最后通过 MCP 给论文写作代理调用，用于规范论文中的句式和证据边界。

现有新增模块包括：

- `scripts/literature_pipeline.py`：OpenAlex/Crossref/arXiv 检索、去重、OA PDF 下载、Obsidian paper notes 和 daily notes 更新。
- `scripts/build_corpus.py`：从 Obsidian paper notes 和可选 PDF 中抽取句子语料。
- `scripts/literature_mcp_server.py`：MCP server，提供语料检索、句式建议、paper context 和句子风险检查。
- `examples/literature-config.example.json`：配置样例。
- `PROJECT_INTRODUCTION.md`：项目介绍。

## 任务目标

请把该项目完善到“可发布、可安装、可日常使用”的水平。

## 必做事项

1. 包装与安装
   - 复核现有 `pyproject.toml` 和 console scripts：`litwiki-discover`、`litwiki-build-corpus`、`litwiki-mcp`、`litwiki-lint`。
   - 如需调整包结构，必须保留现有脚本入口兼容性。

2. 数据模型与测试
   - 为论文记录、配置和语料行建立清晰的数据模型。
   - 扩展现有 pytest 测试，继续覆盖 DOI/arXiv/title 去重、OpenAlex abstract inverted index 还原、Obsidian note 生成、corpus sentence split、MCP search ranking、lint corpus readiness。
   - 保持离线 fixture，测试不能依赖实时网络。

3. 检索源增强
   - 保持默认免费/公开源。
   - 增加 Semantic Scholar 和 PubMed metadata 支持，做成可配置开关。
   - 不实现也不建议任何绕过付费墙的下载方式。

4. Obsidian schema 增强
   - 增加 `data/discovery/`、`data/corpus/`、`pdfs/` 到 schema 文档。
   - paper note frontmatter 保持可被 Dataview 查询。
   - 生成 topic page 时按 foundational/method/application/survey/candidate 分类。

5. Zotero 集成预留
   - 基于 `references/zotero-integration.md` 实现 Zotero export/import 的接口文档和数据字段。
   - 如本地有 Zotero MCP 或 Better BibTeX export，再实现可选同步；没有则保持 pending，不要伪造 citation key。

6. MCP 质量
   - MCP 返回结果必须包含 `paper_id`、title、journal、evidence_status、source_note。
   - 对 `metadata-only` 或 `abstract-screened` 的内容，MCP 必须明确提示只能作为风格或候选依据，不能作为事实结论。
   - 增加 `get_evidence_boundary` 或等价工具，供写作代理查询可用证据边界。

7. 文档
   - 修复 README 中中文乱码。
   - 增加 Quick Start：初始化库、复制配置、运行 daily update、构建 corpus、启动 MCP。
   - 增加 Windows Task Scheduler 和 GitHub Actions 两种每日更新方式。
   - 增加“合法下载与证据状态”说明。

8. CI
   - 增加 GitHub Actions：lint、pytest、脚本 smoke test。
   - CI 不访问真实外部数据库；使用 fixture。

## 验收标准

- `python -m pytest` 通过。
- `python scripts/literature_pipeline.py --config examples/literature-config.example.json --dry-run` 在 fixture/mock 模式下可验证核心逻辑。
- `python scripts/build_corpus.py --vault <test-vault>` 能生成 `sentences.jsonl`。
- MCP server 能在本地启动，并能通过工具返回 corpus search 结果。
- README、PROJECT_INTRODUCTION、SKILL.md 对新增能力描述一致。
- 所有涉及论文结论的文案都保持证据边界，不把 metadata-only 论文写成 fulltext-read 结论。

## 注意事项

- 不要重写用户的真实 Obsidian vault。
- 不要下载无授权 PDF。
- 不要把自动生成摘要当作已验证证据。
- 不要把 GitHub Actions 配置成会污染仓库历史；如果需要提交每日更新，请使用单独分支或在文档中说明。
