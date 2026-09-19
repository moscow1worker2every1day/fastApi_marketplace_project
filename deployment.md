# Инструкция по запуску и развёртыванию

Документ описывает локальный запуск FastAPI Marketplace через Docker Compose, e2e-стек и (опционально) приложения с хоста. Обзор архитектуры: [README.md](./README.md).

---

## Требования

- [Docker](https://docs.docker.com/get-docker/) и Docker Compose v2
- (Опционально) Python **3.12+**, [uv](https://github.com/astral-sh/uv) — для локального запуска приложений без контейнеров
- (Опционально) OpenSSL — для генерации JWT-ключей user_service

---

## 1. Подготовка окружения

### 1.1. Корневой `.env`

Compose подставляет `${VAR}` из корневого `.env`.

```bash
cp .env.example .env
```

Типичные значения (dev):

| Переменная | Назначение | Пример |
|------------|------------|--------|
| `USER_APP_EXTERNAL_PORT` | Порт user_service | `8000` |
| `PRODUCT_APP_EXTERNAL_PORT` | Порт product_service | `8001` |
| `CART_APP_EXTERNAL_PORT` | Порт cart_service | `8002` |
| `USER_POSTGRES_PORT` | Postgres user на хосте | `5432` |
| `PRODUCT_POSTGRES_PORT` | Postgres product на хосте | `5434` |
| `RABBITMQ_USER` / `RABBITMQ_PASSWORD` | Учётка RabbitMQ | см. `.env.example` |

### 1.2. Runtime-конфиг сервисов

| Файл | Когда используется |
|------|--------------------|
| `services/<service>/.env.docker` | Контейнеры (`postgres_*`, `rabbitmq`, `redis`) |
| `services/<service>/.env` | uvicorn / pytest с хоста (`localhost`) |
| `services/<service>/.env.test` | Тесты внутри сервиса |
| `.env.e2e` (из `.env.e2e.example`) | e2e Compose + URL для pytest |

Перед запуском сверьте RabbitMQ-учётки, JWT-пути и **одинаковые** `MQ_PRODUCT_EXCHANGE` / `MQ_PRODUCT_ROUTING_KEY` у product и cart (ожидаются события `product.deleted`, `product.unavailable`, …).

### 1.3. JWT-ключи (user_service)

```bash
cd services/user_service/keys

openssl genrsa -out jwt-private.pem 2048
openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
```

Пути должны совпадать с `.env` / `.env.docker`. Каталог `keys` копируется в Docker-образ user_service.

---

## 2. Запуск через Docker Compose (dev)

Из **корня** проекта:

```bash
docker compose up --build
# или в фоне:
docker compose up --build -d
```

Остановка (данные в volumes сохраняются):

```bash
docker compose down
```

С удалением volumes:

```bash
docker compose down -v
```

### Что поднимается

| Сервис Compose | Описание | Порты на хосте |
|----------------|----------|----------------|
| `postgres_user` | БД пользователей | `${USER_POSTGRES_PORT}` → 5432 (обычно **5432**) |
| `postgres_product` | БД каталога | `${PRODUCT_POSTGRES_PORT}` → 5432 (обычно **5434**) |
| `rabbitmq` | Брокер + Management UI | **5672**, **15672** |
| `redis` | Корзина / опциональный кэш | **6379** |
| `user_service` | Auth + пользователи | **8000** |
| `product_service` | Каталог | **8001** |
| `cart_service` | Корзина | **8002** |

**Не в Compose:** `order_service` (модели и Alembic есть, HTTP API — заготовка).

Приложения ждут healthy зависимости (`depends_on` + healthcheck). В dev включены bind-mount исходников и `uvicorn --reload`.

---

## 3. Проверка работоспособности

| Ресурс | URL |
|--------|-----|
| User Swagger | http://localhost:8000/docs |
| Product Swagger | http://localhost:8001/docs |
| Cart Swagger | http://localhost:8002/docs |
| User health | http://localhost:8000/healthcheck |
| Product health | http://localhost:8001/healthcheck |
| Cart health | http://localhost:8002/healthcheck |
| RabbitMQ UI | http://localhost:15672 |

Логин Management UI — `RABBITMQ_USER` / `RABBITMQ_PASSWORD` из корневого `.env`.

```bash
curl -fsS http://localhost:8000/healthcheck
curl -fsS http://localhost:8001/healthcheck
curl -fsS http://localhost:8002/healthcheck
```

---

## 4. Миграции и схема БД

### user_service

При старте — Alembic `upgrade head`. Есть начальная ревизия (`users`, enum `user_role`).

```bash
docker compose exec user_service alembic upgrade head
```

### product_service

При старте — Alembic `upgrade head`. Есть начальная ревизия (`categories`, `products`).

```bash
docker compose exec product_service alembic upgrade head
```

### order_service

При старте — Alembic `upgrade head` (lifespan). Есть начальная ревизия (`orders`, `order_items`). Сервис пока не в Compose — нужен доступный Postgres в env:

```bash
cd services/order_service
alembic upgrade head
```

---

## 5. Seed пользователей (опционально)

```bash
docker compose exec user_service python -m scripts.seed_users
```

Флаги — в `services/user_service/scripts/`.

---

## 6. Основные API (кратко)

### user_service (`:8000`)

- `POST /auth/sign_up`, `POST /auth/sign_in`, `POST /auth/refresh`
- CRUD пользователей, `/users/account/my_account/`
- `GET /healthcheck`

### product_service (`:8001`)

- CRUD `/products`, `/categories`
- Удаление товара: soft / hard (`mode`) → публикация событий в RabbitMQ
- Создание товара → RPC в user_service (роль `seller`)
- `GET /healthcheck`

### cart_service (`:8002`)

Префикс `/cart`:

- `GET /cart/{user_id}`
- `POST /cart/{user_id}/{product_id}`
- `PUT /cart/{user_id}/change/{product_id}`
- `DELETE /cart/{user_id}/remove/{product_id}`
- `DELETE /cart/{user_id}/clear`
- Consumer: при `product.deleted` / `product.unavailable` убирает позиции из корзин
- `GET /healthcheck`

---

## 7. Локальный запуск приложений (хост + infra в Docker)

```bash
docker compose up -d postgres_user postgres_product rabbitmq redis
```

```bash
cd services/user_service   # или product_service / cart_service
uv sync
# .env → localhost и порты как в корневом Compose
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Порты должны совпадать с пробросом Compose (часто Postgres user `5432`, product `5434`, Redis `6379`, RabbitMQ `5672`).

---

## 8. Тесты

### Unit / integration (внутри сервиса)

```bash
cd services/user_service && uv run pytest
cd services/product_service && uv run pytest
```

Нужны корректные `.env.test` и (для integration) поднятая инфраструктура.

### E2E (интеграция сервисов)

Корневой пакет `tests/e2e` бьёт по HTTP в user / product / cart.

| Файл / каталог | Назначение |
|----------------|------------|
| `docker-compose.e2e.yml` | Overlay: без `--reload`, healthcheck 5s, свои `container_name`/volumes/порты |
| `.env.e2e.example` | Порты Compose (**18xxx**) + URL для pytest |
| `tests/e2e/` | Фикстуры, wait-for-health, сценарии |
| `scripts/e2e/run.sh` | `up -d [--build]` → `pytest tests/e2e` |
| `scripts/e2e/run.ps1` | то же (`-NoBuild`) |

Сценарии:

| Модуль | Что проверяет |
|--------|----------------|
| `test_smoke_health` | `/healthcheck` всех сервисов, smoke category CRUD |
| `test_users_and_roles` | Регистрация, роли, доступ |
| `test_products` | Каталог |
| `test_user_product_rpc` | Создание товара seller через RabbitMQ RPC |
| `test_cart` | CRUD корзины; hard/soft delete товара убирает позиции |

```bash
./scripts/e2e/run.sh
./scripts/e2e/run.sh --no-build

.\scripts\e2e\run.ps1
.\scripts\e2e\run.ps1 -NoBuild
```

Стек после тестов не гасится. Остановка:

```bash
docker compose --env-file .env.e2e -f docker-compose.yml -f docker-compose.e2e.yml -p marketplace-e2e down -v
```

Перед первым e2e: JWT-ключи и согласованные `.env.docker` (как для обычного Compose). При отсутствии `.env.e2e` скрипты копируют его из `.env.e2e.example`.

Можно гонять pytest против обычного `docker compose up`, если URL в `.env.e2e` указать на `8000`/`8001`/`8002`.

---

## 9. Messaging (кратко)

| Поток | Механизм | Назначение |
|-------|----------|------------|
| product → user | RPC, durable queue `user.get_user_by_id.seller` | Проверка seller при создании товара |
| product → cart | Topic exchange (`MQ_PRODUCT_EXCHANGE`), keys `product.*` | Удаление/недоступность товара → очистка позиций корзины |

Настройки exchange/routing key должны совпадать в `product_service` и `cart_service` `.env.docker`.

---

## 10. Типичные проблемы

| Симптом | Что проверить |
|---------|----------------|
| Сервис не стартует | `docker compose logs -f user_service` / `product_service` / `cart_service` |
| Ошибка БД | Health Postgres; логин/БД в `.env` и `.env.docker` |
| Ошибка RabbitMQ / Redis | Контейнеры healthy; host в docker-env = `rabbitmq` / `redis` |
| 401 / JWT | Файлы `jwt-*.pem` и пути в настройках |
| Порт занят | Смените `*_EXTERNAL_PORT` в `.env` или в `.env.e2e` |
| E2E timeout на health | `docker compose -p marketplace-e2e ps` / `logs`; `E2E_HEALTH_TIMEOUT_SEC` |
| Товар не уходит из корзины | Совпадение exchange/routing key; логи consumer в `cart_service` |
| Конфликт e2e и dev | E2e-порты по умолчанию `18000+`, RabbitMQ `5673`, Redis `6380` |

---

## 11. Production (Compose overlay)

Образы собираются multi-stage через `uv sync --frozen`, процесс под non-root `app`, `CMD` с `--workers`. JWT-ключи **не** кладутся в образ — в prod монтируются read-only.

```bash
cp .env.prod.example .env.prod
# Заполнить пароли; сверить RABBITMQ_* и Postgres с services/*/.env.docker
# JWT-ключи: services/user_service/keys/jwt-{private,public}.pem

docker compose --env-file .env.prod \
  -f docker-compose.yml -f docker-compose.prod.yml \
  -p marketplace-prod up --build -d
```

Что делает `docker-compose.prod.yml`:

| Изменение | Зачем |
|-----------|--------|
| Без bind-mount исходников | код только из образа |
| `--workers` вместо `--reload` | prod uvicorn |
| Порты Postgres / Redis / RabbitMQ не публикуются | не торчат наружу |
| App-порты на `127.0.0.1` | доступ с хоста / через reverse-proxy |
| Volume `rabbitmq_data` | персистентность брокера |
| `mem_limit` / `cpus`, `no-new-privileges` | лимиты и hardening |
| Healthcheck ~15s | быстрее детект падений |

Проверка с хоста:

```bash
curl -fsS http://127.0.0.1:8000/healthcheck
curl -fsS http://127.0.0.1:8001/healthcheck
curl -fsS http://127.0.0.1:8002/healthcheck
```

Остановка:

```bash
docker compose --env-file .env.prod \
  -f docker-compose.yml -f docker-compose.prod.yml \
  -p marketplace-prod down
```

Дальше для боевого контура: reverse-proxy (Nginx / Traefik) + TLS, секреты вне git, метрики/логи, в CI — unit + `./scripts/e2e/run.sh`.
