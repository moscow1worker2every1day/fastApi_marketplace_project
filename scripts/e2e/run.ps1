#Requires -Version 5.1
<#
.SYNOPSIS
  Поднять e2e-стек и запустить pytest.
.EXAMPLE
  .\scripts\e2e\run.ps1
  .\scripts\e2e\run.ps1 -NoBuild
#>
param([switch]$NoBuild)

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot "..\.."))

if (-not (Test-Path ".env.e2e")) {
    Copy-Item ".env.e2e.example" ".env.e2e"
    Write-Host "Created .env.e2e from .env.e2e.example"
}

$up = @(
    "compose", "--env-file", ".env.e2e",
    "-f", "docker-compose.yml", "-f", "docker-compose.e2e.yml",
    "-p", "marketplace-e2e", "up", "-d"
)
if (-not $NoBuild) { $up += "--build" }

Write-Host "Starting e2e stack..."
& docker @up
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Installing e2e deps..."
if (Get-Command uv -ErrorAction SilentlyContinue) {
    & uv sync
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "Running pytest..."
    & uv run pytest tests/e2e
} else {
    & python -m pip install httpx "pytest>=9" pytest-asyncio python-dotenv
    Write-Host "Running pytest..."
    & python -m pytest tests/e2e
}

exit $LASTEXITCODE
