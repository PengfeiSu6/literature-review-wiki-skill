from __future__ import annotations


def init_project() -> int:
    from scripts.init_lit_review_project import main

    return main()


def discover() -> int:
    from scripts.literature_pipeline import main

    return main()


def daily_json() -> int:
    from scripts.daily_json_to_obsidian import main

    return main()


def build_corpus() -> int:
    from scripts.build_corpus import main

    return main()


def lint() -> int:
    from scripts.lint_lit_review_wiki import main

    return main()


def mcp() -> int:
    from scripts.literature_mcp_server import main

    return main()
