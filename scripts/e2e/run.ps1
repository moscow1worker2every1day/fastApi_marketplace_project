#Requires -Version 5.1
<#
.SYNOPSIS
  Поднять e2e-стек, дождаться healthcheck и прогнать pytest.
.EXAMPLE
  .\scripts\e2e\run.ps1
  .\scripts\e2e\run.ps1 -SkipDown
  .\scripts\e2e\run.ps1 -NoBuild -SkipDown   # если Docker Hub недоступен / битый cache
#>
param(
    [switch]$SkipUp,
    [switch]$SkipDown,
    [switch]$NoBuild,
    [string]$PytestArgs = "tests/e2e"
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $Root

$EnvFile = Join-Path $Root ".env.e2e"
if (-not (Test-Path $EnvFile)) {
    Copy-Item (Join-Path $Root ".env.e2e.example") $EnvFile
    Write-Host "Created .env.e2e from .env.e2e.example"
}

$Compose = @(
    "compose",
    "--env-file", ".env.e2e",
    "-f", "docker-compose.yml",
    "-f", "docker-compose.e2e.yml",
    "-p", "marketplace-e2e"
)

function Invoke-E2eUp {
    param([switch]$Build)
    $args = @("up", "-d")
    if ($Build) { $args = @("up", "--build", "-d") }
    & docker @Compose @args
    return $LASTEXITCODE
}

if (-not $SkipUp) {
    Write-Host "Starting e2e stack..."
    $code = Invoke-E2eUp -Build:(!$NoBuild)
    if ($code -ne 0) {
        # Часто на Windows: битый BuildKit cache ("parent snapshot ... does not exist")
        Write-Host "Compose up failed. Pruning BuildKit cache and retrying once..."
        & docker builder prune -af | Out-Null
        $code = Invoke-E2eUp -Build:(!$NoBuild)
        if ($code -ne 0) { exit $code }
    }
}

Write-Host "Installing e2e deps..."
if (Get-Command uv -ErrorAction SilentlyContinue) {
    & uv sync
    $PytestCmd = { param($a) & uv run pytest @a }
} else {
    & python -m pip install httpx "pytest>=9" pytest-asyncio python-dotenv
    $PytestCmd = { param($a) & python -m pytest @a }
}

Write-Host "Running pytest $PytestArgs ..."
$argsList = $PytestArgs -split "\s+"
& $PytestCmd $argsList
$TestExit = $LASTEXITCODE

if (-not $SkipDown) {
    Write-Host "Tearing down e2e stack..."
    & docker @Compose down -v
}

exit $TestExit
