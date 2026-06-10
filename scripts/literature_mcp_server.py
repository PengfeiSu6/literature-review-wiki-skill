#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.literature_mcp_core import evidence_boundary, phrase_suggestions, search_rows
except ImportError:
    from literature_mcp_core import evidence_boundary, phrase_suggestions, search_rows


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MCP server for a local Obsidian literature corpus.")
    parser.add_argument("--vault", required=True, help="Wiki root directory, often <vault>/Literature.")
    return parser.parse_args(argv)


def create_server(vault: Path) -> Any:
    try:
        from mcp.server.fastmcp import FastMCP  # type: ignore
    except ImportError:
        print("Missing dependency: install the MCP Python SDK with `pip install mcp` or `pip install -e .[mcp]`.", file=sys.stderr)
        raise SystemExit(2)

    vault = vault.resolve()
    corpus_path = vault / "data" / "corpus" / "sentences.jsonl"
    mcp = FastMCP("literature-review-wiki")

    @mcp.tool()
    def search_literature_corpus(query: str, limit: int = 8, evidence_status: str = "") -> list[dict[str, Any]]:
        """Search sentence-level corpus examples by topic, phrase, journal, or rhetorical wording."""
        return search_rows(corpus_path, query=query, limit=limit, evidence_status=evidence_status)

    @mcp.tool()
    def suggest_academic_phrases(rhetorical_function: str = "general-academic", limit: int = 10) -> list[dict[str, str]]:
        """Return corpus-backed sentence examples for a rhetorical function such as background, gap, method, or result."""
        return phrase_suggestions(corpus_path, rhetorical_function, limit)

    @mcp.tool()
    def get_paper_context(paper_id: str) -> str:
        """Return the Obsidian paper note body for a known paper_id."""
        note = vault / "papers" / f"{paper_id}.md"
        if not note.exists():
            return f"No paper note found for {paper_id}"
        return note.read_text(encoding="utf-8", errors="replace")

    @mcp.tool()
    def check_sentence_against_corpus(sentence: str, query: str = "", limit: int = 5) -> dict[str, Any]:
        """Compare a draft sentence with corpus examples and return conservative style guidance."""
        lookup = query or sentence
        examples = search_rows(corpus_path, lookup, limit=limit)
        risky = []
        lower = sentence.lower()
        for word in ["prove", "state of the art", "comprehensive", "all recent work"]:
            if word in lower:
                risky.append(f"Guard or evidence-check wording: '{word}'.")
        return {
            "draft_sentence": sentence,
            "style_examples": examples,
            "warnings": risky,
            "evidence_boundary": "Use corpus sentences as style examples. Do not reuse findings unless the linked paper note is fulltext-read.",
        }

    @mcp.tool()
    def get_evidence_boundary(evidence_status: str = "") -> dict[str, str]:
        """Explain how a paper or corpus row may be used at a given evidence status."""
        statuses = ["metadata-only", "abstract-screened", "fulltext-read", "citation-chain", "excluded"]
        if evidence_status:
            return {evidence_status: evidence_boundary(evidence_status)}
        return {status: evidence_boundary(status) for status in statuses}

    return mcp


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    server = create_server(Path(args.vault))
    server.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
