from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_python(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def assert_success(result: subprocess.CompletedProcess[str]) -> None:
    assert result.returncode == 0, result.stdout + result.stderr


def test_pyproject_declares_package_and_console_scripts() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["name"] == "literature-review-wiki-skill"
    assert pyproject["project"]["requires-python"] == ">=3.11"
    assert pyproject["project"]["dependencies"] == []
    assert pyproject["tool"]["setuptools"]["package-dir"] == {"": "src"}

    scripts = pyproject["project"]["scripts"]
    assert scripts["litwiki-init"] == "literature_review_wiki.cli.init_project:main"
    assert scripts["litwiki-daily-json"] == "literature_review_wiki.cli.daily_json:main"
    assert scripts["litwiki-lint"] == "literature_review_wiki.cli.lint_wiki:main"


def test_package_module_entrypoints_initialize_and_lint_temp_wiki(tmp_path: Path) -> None:
    wiki_root = tmp_path / "Literature"

    init_result = run_python(
        "-m",
        "literature_review_wiki.cli.init_project",
        "--root",
        str(wiki_root),
        "--topic",
        "industrial energy flexibility",
        "--zotero-collection",
        "industrial energy flexibility",
    )
    assert_success(init_result)

    config = json.loads((wiki_root / "config" / "literature-review-config.json").read_text(encoding="utf-8"))
    assert config["topic_slug"] == "industrial-energy-flexibility"
    assert config["evidence_statuses"][:3] == ["metadata-only", "abstract-screened", "fulltext-read"]

    lint_result = run_python(
        "-m",
        "literature_review_wiki.cli.lint_wiki",
        "--vault",
        str(wiki_root),
    )
    assert_success(lint_result)
    assert "Literature wiki lint passed" in lint_result.stdout


def test_legacy_scripts_remain_executable_with_temp_paths(tmp_path: Path) -> None:
    wiki_root = tmp_path / "LegacyLiterature"

    init_result = run_python(
        str(ROOT / "scripts" / "init_lit_review_project.py"),
        "--root",
        str(wiki_root),
        "--topic",
        "thermal storage",
    )
    assert_success(init_result)

    feed_path = tmp_path / "latest.json"
    feed_path.write_text(
        json.dumps(
            {
                "papers": [
                    {
                        "title": "Flexible Industrial Heat Scheduling",
                        "authors": ["A. Researcher"],
                        "published": "2025-03-01",
                        "doi": "10.1000/example",
                        "url": "https://example.org/paper",
                        "summary": "Candidate metadata only.",
                        "categories": ["energy"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    daily_result = run_python(
        str(ROOT / "scripts" / "daily_json_to_obsidian.py"),
        "--input",
        str(feed_path),
        "--vault",
        str(wiki_root),
        "--date",
        "2026-06-10",
        "--source-name",
        "test-feed",
    )
    assert_success(daily_result)
    assert (wiki_root / "daily" / "2026-06-10.md").exists()

    lint_result = run_python(
        str(ROOT / "scripts" / "lint_lit_review_wiki.py"),
        "--vault",
        str(wiki_root),
    )
    assert_success(lint_result)
