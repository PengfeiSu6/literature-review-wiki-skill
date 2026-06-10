# 项目介绍：Literature Review Wiki Skill

`literature-review-wiki-skill` 是一个面向科研写作的本地优先文献知识库工具。它把论文发现、开放获取 PDF 下载、Obsidian 文献库维护、语料库构建和 MCP 写作辅助连接到同一套可复现流程中。

## 目标

这个项目的目标不是简单保存论文列表，而是建立一个可持续更新、证据边界清楚、可被写作代理调用的领域文献系统：

- 按 topic 和高水平期刊白名单检索相关论文。
- 只下载官方开放获取、arXiv、PubMed Central 或用户有权访问的 PDF。
- 在 Obsidian 中生成 paper notes、daily updates、topics、claims 和 reviews。
- 用 `seen_papers.json` 做每日去重，保证增量更新不会重复建库。
- 从摘要、笔记和本地 PDF 中抽取句子，形成领域写作语料库。
- 通过 MCP 暴露语料检索、句式建议和句子风险检查工具，服务后续论文写作。

## 核心原则

1. Zotero 是文献条目的长期来源，Obsidian 是知识组织和综述写作层。
2. `metadata-only`、`abstract-screened`、`fulltext-read` 必须严格区分。
3. 未读全文的论文只能作为候选、检索日志或语料风格样本，不能支撑论文中的事实性结论。
4. PDF 下载只走合法开放获取路径，不绕过出版社访问控制。
5. MCP 返回的是“写作风格证据”和“可追溯上下文”，不是自动生成的不可核验结论。

## 新增功能模块

### 1. 配置驱动的每日文献更新

脚本：`scripts/literature_pipeline.py`

功能：

- 从 OpenAlex、Crossref、arXiv 获取论文元数据。
- 可选从 Semantic Scholar 和 PubMed 获取 metadata。
- 支持 topic 查询、别名、期刊白名单、期刊正则匹配和时间窗口。
- 对 DOI、arXiv ID、标题做去重。
- 保存原始发现结果到 `data/discovery/YYYY-MM-DD.json`。
- 新论文写入 `papers/<paper_id>.md`。
- 每日增量写入 `daily/YYYY-MM-DD.md`。
- 可选下载开放获取 PDF 到 `pdfs/`。

### 2. Obsidian 语料库构建

脚本：`scripts/build_corpus.py`

功能：

- 从 paper notes 的摘要、方法、证据和限制部分抽取句子。
- 可选用 `pypdf` 读取本地 PDF 文本。
- 标注句子的 rhetorical function，例如 background、gap、method、result。
- 输出 `data/corpus/sentences.jsonl` 和 `data/corpus/phrase-patterns.md`。

### 3. MCP 写作辅助服务

脚本：`scripts/literature_mcp_server.py`

MCP tools：

- `search_literature_corpus`：按关键词检索语料句子。
- `suggest_academic_phrases`：按 rhetorical function 给出语料支持的表达方式。
- `get_paper_context`：读取指定 paper note。
- `check_sentence_against_corpus`：检查草稿句子是否有过度表述风险，并返回相似语料。
- `get_evidence_boundary`：说明不同 evidence status 在写作中的可用边界。

## 推荐工作流

1. 用 `init_lit_review_project.py` 初始化 Obsidian 文献库目录。
2. 复制 `examples/literature-config.example.json`，填入真实 topic、期刊名单和 vault 路径。
3. 每天运行 `literature_pipeline.py` 抓取新论文。
4. 运行 `build_corpus.py` 更新语料库。
5. 用 `lint_lit_review_wiki.py` 检查证据状态和结构。
6. 在写作代理中配置 `literature_mcp_server.py`，让论文写作调用本地语料库。

## 工程化完善

- 已加入 `pyproject.toml`，支持 editable install 和 console scripts。
- 已加入 `tests/` 离线 fixture，不依赖实时网络验证核心逻辑。
- 已加入 GitHub Actions CI，执行脚本编译和 pytest。
- 现有脚本入口仍保留，兼容 `python scripts/<name>.py` 用法。

## 项目边界

当前实现是可运行的本地工具骨架，不替代数据库订阅、人工全文阅读或 Zotero 的正式文献管理。它负责把可公开发现的论文可靠地进入本地知识库，并为后续人工筛选和代理写作提供结构化入口。
