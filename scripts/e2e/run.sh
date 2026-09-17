#!/usr/bin/env bash
# Поднять e2e-стек, дождаться healthcheck (в conftest) и прогнать pytest.
# Usage: ./scripts/e2e/run.sh [--skip-up] [--skip-down] [-- pytest args...]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

SKIP_UP=0
SKIP_DOWN=0
PYTEST_ARGS=(tests/e2e)

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-up) SKIP_UP=1; shift ;;
    --skip-down) SKIP_DOWN=1; shift ;;
    --) shift; PYTEST_ARGS=("$@"); break ;;
    *) PYTEST_ARGS=("$@"); break ;;
  esac
done

if [[ ! -f .env.e2e ]]; then
  cp .env.e2e.example .env.e2e
  echo "Created .env.e2e from .env.e2e.example"
fi

COMPOSE=(docker compose --env-file .env.e2e -f docker-compose.yml -f docker-compose.e2e.yml -p marketplace-e2e)

if [[ "$SKIP_UP" -eq 0 ]]; then
  echo "Starting e2e stack..."
  "${COMPOSE[@]}" up --build -d
fi

if command -v uv >/dev/null 2>&1; then
  uv sync
  RUNNER=(uv run pytest)
else
  python -m pip install httpx "pytest>=9" pytest-asyncio python-dotenv
  RUNNER=(python -m pytest)
fi

echo "Running ${RUNNER[*]} ${PYTEST_ARGS[*]} ..."
set +e
"${RUNNER[@]}" "${PYTEST_ARGS[@]}"
TEST_EXIT=$?
set -e

if [[ "$SKIP_DOWN" -eq 0 ]]; then
  echo "Tearing down e2e stack..."
  "${COMPOSE[@]}" down -v
fi

exit "$TEST_EXIT"
