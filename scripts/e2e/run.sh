#!/usr/bin/env bash
# Поднять e2e-стек и запустить pytest.
# Usage: ./scripts/e2e/run.sh [--no-build]
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

NO_BUILD=0
[[ "${1:-}" == "--no-build" ]] && NO_BUILD=1

if [[ ! -f .env.e2e ]]; then
  cp .env.e2e.example .env.e2e
  echo "Created .env.e2e from .env.e2e.example"
fi

cmd=(
  docker compose --env-file .env.e2e
  -f docker-compose.yml -f docker-compose.e2e.yml
  -p marketplace-e2e up -d
)
[[ "$NO_BUILD" -eq 0 ]] && cmd+=(--build)

echo "Starting e2e stack..."
"${cmd[@]}"

echo "Installing e2e deps..."
if command -v uv >/dev/null 2>&1; then
  uv sync
  echo "Running pytest..."
  uv run pytest tests/e2e
else
  python -m pip install httpx "pytest>=9" pytest-asyncio python-dotenv
  echo "Running pytest..."
  python -m pytest tests/e2e
fi
