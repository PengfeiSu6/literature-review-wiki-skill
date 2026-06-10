param(
  [Parameter(Mandatory = $true)]
  [string]$RepoRoot,

  [Parameter(Mandatory = $true)]
  [string]$ConfigPath,

  [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$repo = Resolve-Path -LiteralPath $RepoRoot
$config = Resolve-Path -LiteralPath $ConfigPath
$cfg = Get-Content -Raw -LiteralPath $config | ConvertFrom-Json
$vault = [string]$cfg.wiki_root

& $Python (Join-Path $repo "scripts\literature_pipeline.py") --config $config
& $Python (Join-Path $repo "scripts\build_corpus.py") --vault $vault
& $Python (Join-Path $repo "scripts\lint_lit_review_wiki.py") --vault $vault
