# Literature Review Wiki Workflow

## 1. Intake

Record a topic brief before searching:

- topic name and aliases
- scope boundaries
- seed papers or seed keywords
- preferred disciplines and venues
- inclusion/exclusion criteria
- required output language and citation style
- Zotero collection name
- Obsidian vault path and wiki root

If the topic is broad, split it into 3-7 query facets such as method, application, dataset, benchmark, and review/survey.

## 2. Discovery

Use multiple discovery lanes and keep their outputs separate until deduplication:

- broad metadata search: OpenAlex, Semantic Scholar, Crossref
- preprint search: arXiv, bioRxiv, medRxiv
- domain database: PubMed, IEEE Xplore metadata, DBLP, ACM, Scopus/WoS if the user has access
- citation expansion: references and citing papers for seed papers
- daily feed: `lelouchsola/arXiv-Daily-Summarizer`, `TideDra/zotero-arxiv-daily`, or topic-specific RSS

Save raw search outputs when possible. Do not collapse candidate papers into review claims during discovery.

## 3. Screening

Use two passes:

1. Title/abstract pass: mark `candidate`, `excluded`, or `needs-fulltext`.
2. Full-text pass: mark `fulltext-read`, extract evidence, and link claims.

Every exclusion should have a short reason. Common reasons: out of scope, wrong domain, no technical contribution, duplicate, not peer-reviewed, unavailable full text, or superseded.

## 4. Ingestion

Use Zotero for canonical metadata:

- add by DOI/arXiv ID/PMID when possible
- attach only authorized open-access PDFs
- store citation key, DOI, URL, PDF URL, source, and collection
- use Better BibTeX when citation keys matter
- use Zotero Integration or exported Markdown to connect notes to Obsidian

If Zotero tooling is unavailable, create paper stubs in Obsidian but mark `zotero_status: pending`.

## 5. Obsidian Wiki Update

For each accepted paper:

- create or update one `papers/` note
- link it to one or more `topics/` pages
- add extracted evidence to `claims/` only after full-text reading
- update `reviews/working-review.md` only after the claim map is updated
- log daily additions in `daily/YYYY-MM-DD.md`

Keep summary, evidence, critique, and relevance separate inside paper notes.

## 6. Literature Review Update

Update in this order:

1. `topics/`: taxonomy and paper placement
2. `claims/`: evidence-backed claims and conflicts
3. `reviews/working-review.md`: prose synthesis
4. `reviews/gaps.md`: open problems and uncertainty
5. `dashboard.md`: current status and next actions

Use wording that matches evidence. Example: "Candidate papers suggest..." for metadata-only evidence; "Full-text evidence supports..." only after full-text reading.

## 7. Verification

Before treating the review as current:

- run `scripts/lint_lit_review_wiki.py`
- check that new claims cite paper notes
- check that paper notes have source URLs or stable identifiers
- check that daily additions are represented in topic pages
- check that excluded papers did not silently influence conclusions
