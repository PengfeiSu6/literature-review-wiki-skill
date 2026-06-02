# Evidence and Access Policy

## Access

Allowed default sources:

- arXiv and other author-posted preprints
- PubMed Central and official open-access PDFs
- publisher open-access PDFs
- Unpaywall-discovered open-access locations
- institutional or user-provided PDFs when the user confirms they have access rights

Do not use unauthorized sources or bypass publisher access controls.

## Evidence Statuses

- `metadata-only`: search result or metadata only
- `abstract-screened`: abstract reviewed
- `fulltext-read`: full text reviewed
- `citation-chain`: found through reference/citation expansion
- `excluded`: screened out

## Claim Rules

- A literature-review claim must cite at least one `fulltext-read` paper note.
- A trend claim should cite multiple papers unless clearly presented as a hypothesis.
- A gap claim should distinguish "not found in this search" from "absent in the literature".
- A benchmark or method comparison should include evaluation conditions, dataset/domain, and metric if available.
- Do not turn model-generated summaries into evidence unless checked against the paper.

## Review Language

Use guarded wording when evidence is incomplete:

- metadata-only: "candidate", "appears related", "requires screening"
- abstract-screened: "the abstract suggests", "reported focus"
- fulltext-read: "the paper reports", "the authors demonstrate", "the method evaluates"

Avoid unsupported wording:

- "proves"
- "state of the art" without a benchmark
- "comprehensive" without a search protocol
- "all recent work" without explicit search dates and databases
