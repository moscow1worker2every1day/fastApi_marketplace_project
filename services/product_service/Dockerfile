# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /build
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.12-slim AS runtime

RUN groupadd --system --gid 1000 app \
    && useradd --system --uid 1000 --gid app --home /code --shell /usr/sbin/nologin app \
    && apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# venv вне /code — иначе bind-mount в dev/e2e перекрывает зависимости
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/code \
    PATH="/opt/venv/bin:$PATH" \
    APP_HOST=0.0.0.0 \
    APP_INTERNAL_PORT=8001 \
    APP_WORKERS=2

COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app app ./app
COPY --chown=app:app alembic ./alembic
COPY --chown=app:app alembic.ini .

USER app
EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=25s --retries=5 \
    CMD curl -fsS "http://127.0.0.1:${APP_INTERNAL_PORT}/healthcheck" || exit 1

CMD ["sh", "-c", "exec uvicorn app.main:app --host ${APP_HOST} --port ${APP_INTERNAL_PORT} --workers ${APP_WORKERS}"]
