FROM python:3.12-slim

WORKDIR /code

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY keys ./keys
COPY alembic ./alembic
COPY alembic.ini .
# Scripts for users creation (develop)
COPY scripts ./scripts

ENV PYTHONPATH=/code
