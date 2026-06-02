# Daily Automation

## Preferred Codex Path

If the user asks to create, inspect, update, or delete recurring checks, first search for the `automation_update` tool and use it if available.

The recurring task should:

1. fetch or run the daily paper source
2. write raw results
3. convert new records into Obsidian notes
4. mark new high-priority papers for Zotero import
5. update topic pages and the working review only when evidence status allows it
6. produce a short daily change summary

## GitHub Actions Pattern

Use this when the user wants a cloud-run daily feed:

```yaml
on:
  schedule:
    - cron: "17 1 * * *"
  workflow_dispatch:
```

For Asia/Shanghai, `17 1 * * *` UTC runs around 09:17 local time. Adjust the cron if the user wants a different daily window.

## arXiv-Daily-Summarizer Integration

`lelouchsola/arXiv-Daily-Summarizer` is useful as a daily radar:

- workflow: `.github/workflows/build_daily_site.yml`
- local entry: `python -m scripts.build_daily_site`
- output: `site/latest.json` and `site/index.html`
- default env examples: `ARXIV_CATEGORIES`, `ENABLED_SOURCES`, `LOOKBACK_DAYS`, `MAX_RESULTS`, `SUMMARY_COUNT`, `TARGET_TIMEZONE`

Integration steps:

1. Run the upstream workflow or fetch the public `site/latest.json`.
2. Save the JSON under the wiki `data/` folder.
3. Run `scripts/daily_json_to_obsidian.py --input latest.json --vault <vault>`.
4. Import selected papers into Zotero.
5. Update local history because the upstream daily site intentionally does not preserve cross-day history.

## Local Scheduler Pattern

For a Windows local vault, use Task Scheduler to run a PowerShell command that calls Python with absolute paths. Keep API keys in environment variables or a local `.env` outside Obsidian notes.

The job should be idempotent. It must not duplicate paper notes when a DOI, arXiv ID, or known URL already exists.
