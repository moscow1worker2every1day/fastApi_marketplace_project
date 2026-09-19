# FastAPI Marketplace

Микросервисный бэкенд маркетплейса на **FastAPI**: пользователи и аутентификация, каталог товаров и категорий, корзина и заготовки под заказы. Сервисы изолированы по данным (database-per-service), общаются по HTTP и через **RabbitMQ**, поднимаются через **Docker Compose**. Есть black-box **e2e**-набор против полного стека.

Подробная инструкция по запуску и окружению: [deployment.md](./deployment.md).

---

## Зачем этот проект

- Демонстрирует связку **API + Postgres + SQLAlchemy + RabbitMQ + Redis + JWT + Docker**, типичную для e-commerce.
- Полезен как основа для внедрения доработок: заказы, платежи, API Gateway, наблюдаемость, CI.

---

## Архитектура сервисов

| Сервис | Порт (dev) | Назначение | Статус |
|--------|------------|------------|--------|
| **user_service** | `8000` | Регистрация, JWT (RS256), роли, CRUD пользователей | Готов |
| **product_service** | `8001` | Категории и товары, фильтры, soft delete, RPC к user, события каталога | Готов |
| **cart_service** | `8002` | Корзина в Redis, реакция на `product.deleted` / `product.unavailable` | Готов |
| **order_service** | — | Модели/Alembic есть, API — заготовка | Не в Compose |

**Инфраструктура в Compose:** PostgreSQL ×2 (user / product), RabbitMQ (+ Management UI), Redis.

```
Клиент (HTTP)
    ├─► user_service  ──► Postgres (users)
    │         ▲
    │         │ RabbitMQ RPC: проверка seller
    │         │
    └─► product_service ──► Postgres (products)
              │              (+ опциональный Redis-кэш)
              │ RabbitMQ topic: product.deleted / product.unavailable / …
              ▼
         cart_service ──► Redis
```

---

## Сильные стороны

1. **Разделение ответственности** — у каждого сервиса свой домен и своя БД (или Redis для корзины).
2. **Production-minded user_service** — JWT RS256, refresh-токены, RBAC (`admin` / `user` / `seller`), healthcheck, логи, seed, unit/integration-тесты.
3. **Каталог** — иерархия категорий, пагинация/фильтры, soft/hard delete, OpenAPI, Alembic, опциональный Redis-кэш.
4. **Два стиля messaging** — RPC request/reply (seller check) и pub/sub события каталога → синхронизация корзин.
5. **Cart в стеке** — Redis + consumer на topic exchange; e2e проверяет побочные эффекты удаления товара.
6. **DevOps** — Compose с healthcheck/`depends_on`, `.env` + `.env.docker`, e2e-overlay с отдельными портами (параллельно с dev).
7. **Стек** — Python 3.12+, FastAPI, SQLAlchemy 2 async, Pydantic Settings, **uv**.

---

## Применённые паттерны и практики

| Паттерн / практика | Где проявляется |
|--------------------|-----------------|
| **Микросервисы + Database per service** | Отдельные Postgres для user и product; Redis для cart |
| **Слоистая архитектура** | `api` → `services` → `repositories` → `storage` |
| **Dependency Injection** | FastAPI `Depends`, typed-зависимости (`AdminUserDep`, `SessionDep`, …) |
| **Repository** | User / Product / Category / Cart |
| **RPC** | aio-pika, queue `user.get_user_by_id.seller` |
| **Event-driven (pub/sub)** | Exchange `Product`, routing keys `product.*` → cart consumer |
| **Кэширование** | Декоратор Redis-кэша в product_service (`REDIS_ENABLED`) |
| **RBAC** | Роли и dependency-guards |
| **Lifespan startup** | Проверка БД/MQ/Redis, миграции, фоновый consumer |
| **Middleware** | CORS, логирование запросов |
| **Healthchecks** | `/healthcheck` + healthcheck контейнеров |
| **Soft delete** | Товары: `mode=soft` / полное удаление + события в MQ |
| **Black-box e2e** | `tests/e2e` + httpx против Compose |
| **Конфигурация** | Pydantic Settings; Compose / runtime / e2e env разделены |

---

## Быстрый старт

```bash
# из корня (если нет .env — скопируйте .env.example → .env)
cp .env.example .env   # при необходимости
docker compose up --build
```

| Что | URL |
|-----|-----|
| User API / Swagger | http://localhost:8000/docs |
| Product API / Swagger | http://localhost:8001/docs |
| Cart API / Swagger | http://localhost:8002/docs |
| RabbitMQ Management | http://localhost:15672 |

Остановка: `docker compose down`.

Перед первым запуском нужны JWT-ключи в `services/user_service/keys/` — см. [deployment.md](./deployment.md).

---

## E2E-тесты

Black-box pytest + httpx: smoke health, роли/auth, каталог, RPC seller, корзина и реакция на удаление товара.

| Скрипт | Поведение |
|--------|-----------|
| `scripts/e2e/run.sh` | `up -d [--build]` → `pytest tests/e2e` |
| `scripts/e2e/run.ps1` | то же (`-NoBuild` / `--no-build` без пересборки) |

```bash
# Linux / macOS / Git Bash
./scripts/e2e/run.sh
./scripts/e2e/run.sh --no-build

# Windows
.\scripts\e2e\run.ps1
.\scripts\e2e\run.ps1 -NoBuild
```

Стек после прогона остаётся запущенным. Остановка:

```bash
docker compose --env-file .env.e2e -f docker-compose.yml -f docker-compose.e2e.yml -p marketplace-e2e down -v
```

E2E использует **смещённые порты** (по умолчанию `18000` / `18001` / `18002`), чтобы не конфликтовать с dev-стеком. Шаблон: `.env.e2e.example` → `.env.e2e`.

Подробности: [deployment.md](./deployment.md) § E2E.

---

## Стек

- **API:** FastAPI, Uvicorn  
- **БД:** PostgreSQL 16, SQLAlchemy 2 (asyncpg); Alembic в user / product / order  
- **Кэш / корзина:** Redis 7  
- **Очереди:** RabbitMQ 3 (Management)  
- **Auth:** JWT RS256, OAuth2 password flow, bcrypt  
- **Логи:** Loguru  
- **Тесты:** pytest (+ asyncio); e2e в корневом `tests/e2e`  
- **Упаковка / запуск:** uv, Docker, Docker Compose  

---

## Возможные пути развития

1. **Довести order_service** — checkout из корзины, статусы, резерв остатков; saga / transactional outbox; добавить в Compose.
2. **API Gateway / BFF** — единая точка входа, JWT один раз, rate limiting.
3. **Общая аутентификация между сервисами** — JWKS / public key, Bearer на product/cart/order.
4. **Ревизии Alembic для user_service** — сейчас startup опирается на `create_all` при отсутствии versions.
5. **Observability** — Prometheus, OpenTelemetry, correlation id через HTTP и MQ.
6. **CI** — unit-тесты сервисов + `scripts/e2e/run.sh` в pipeline.
7. **Production Docker** — частично: multi-stage + `uv sync --frozen`, `docker-compose.prod.yml`; дальше — reverse-proxy/TLS и order_service в Compose.
8. **Recommendation service** — персональные/популярные рекомендации.
9. **Безопасность** — секреты вне репозитория, ужесточение CORS, минимальный JWT payload.
10. **CI e2e на Windows** — тот же `run.ps1`, что и `run.sh`.

---

## Структура репозитория

```
fastApi_marketplace_project/
├── docker-compose.yml
├── docker-compose.e2e.yml      # overlay: без --reload, быстрый healthcheck, свои порты/имена
├── docker-compose.prod.yml     # overlay: prod (workers, без bind-mount, infra без publish)
├── .env.example                # шаблон для обычного Compose
├── .env.e2e.example            # шаблон для e2e (порты 18xxx)
├── .env.prod.example           # шаблон для production Compose
├── pyproject.toml              # зависимости корневых e2e-тестов
├── tests/e2e/                  # black-box сценарии
├── scripts/e2e/                # run.ps1 / run.sh: up + pytest
├── deployment.md
└── services/
    ├── user_service/
    ├── product_service/
    ├── cart_service/
    └── order_service/
```

---

## Лицензия и вклад

Проект демонстрационный. Удобные точки входа для доработки: `order_service`, общая JWT-валидация между сервисами, CI вокруг e2e.
