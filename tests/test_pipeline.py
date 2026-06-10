from __future__ import annotations

import json
from pathlib import Path

from scripts import literature_pipeline as pipeline


def test_openalex_abstract_inverted_index_round_trip() -> None:
    abstract = pipeline.abstract_from_openalex({"Industrial": [0], "flexibility": [2], "energy": [1]})

    assert abstract == "Industrial energy flexibility"


def test_dedupe_prefers_stable_doi_and_merges_pdf_url() -> None:
    first = pipeline.PaperRecord(
        paper_id="doi-10-0000-example",
        title="Same Paper",
        doi="10.0000/example",
        abstract="A useful abstract.",
    )
    second = pipeline.PaperRecord(
        paper_id="doi-10-0000-example",
        title="Same Paper",
        doi="https://doi.org/10.0000/example".replace("https://doi.org/", ""),
        pdf_url="https://example.org/paper.pdf",
    )

    records = pipeline.dedupe_records([first, second])

    assert len(records) == 1
    assert records[0].pdf_url == "https://example.org/paper.pdf"
    assert records[0].abstract == "A useful abstract."


def test_pipeline_fixture_writes_obsidian_notes(tmp_path: Path) -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "discovery-records.json"
    vault = tmp_path / "Literature"
    config = {
        "topic": "industrial energy flexibility",
        "topic_aliases": ["industrial demand response"],
        "wiki_root": str(vault),
        "fixture_records_path": str(fixture_path),
        "download_open_access_pdfs": False,
        "run_date": "2026-06-10",
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    summary = pipeline.run_pipeline(config_path)

    assert summary["discovered"] == 1
    assert summary["new_records"] == 1
    note = vault / "papers" / "doi-10-0000-example.md"
    assert note.exists()
    text = note.read_text(encoding="utf-8")
    assert "evidence_status: metadata-only" in text
    assert "Industrial energy flexibility" in text
    assert (vault / "daily" / "2026-06-10.md").exists()
    assert (vault / "config" / "literature-review-config.json").exists()


def test_pubmed_article_records_parse_minimal_xml() -> None:
    xml_text = """<?xml version="1.0"?>
    <PubmedArticleSet>
      <PubmedArticle>
        <MedlineCitation>
          <PMID>12345</PMID>
          <Article>
            <ArticleTitle>Industrial flexibility in energy systems</ArticleTitle>
            <Abstract><AbstractText>Flexible loads can support renewable integration.</AbstractText></Abstract>
            <Journal><Title>Energy</Title><JournalIssue><PubDate><Year>2025</Year></PubDate></JournalIssue></Journal>
            <AuthorList><Author><ForeName>Ada</ForeName><LastName>Lovelace</LastName></Author></AuthorList>
          </Article>
        </MedlineCitation>
        <PubmedData><ArticleIdList><ArticleId IdType="doi">10.0000/pubmed</ArticleId></ArticleIdList></PubmedData>
      </PubmedArticle>
    </PubmedArticleSet>
    """

    records = pipeline.pubmed_article_records(xml_text, "industrial flexibility")

    assert len(records) == 1
    assert records[0].pmid == "12345"
    assert records[0].doi == "10.0000/pubmed"
    assert records[0].journal == "Energy"
