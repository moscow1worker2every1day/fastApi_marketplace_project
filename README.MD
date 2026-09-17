# FastAPI Marketplace

Микросервисный бэкенд маркетплейса на **FastAPI**: пользователи и аутентификация, каталог товаров и категорий, корзина и заготовки под заказы. Сервисы изолированы по данным (database-per-service), общаются по HTTP и через **RabbitMQ**, поднимаются через **Docker Compose**.

Подробная инструкция по запуску и окружению: [deployment.md](./deployment.md).

---

## Зачем этот проект

- Демонстрирует связку **API + Postgres + SQLAlchemy + RabbitMQ + Redis + JWT + Docker**, типичную для e-commerce.
- Полезен как основа для внедрения prodaction-features: платежи, AI-рекомендации, API Gateway, наблюдаемость.

---

## Архитектура сервисов

| Сервис | Порт | Назначение | Статус |
|--------|------|------------|--------|
| **user_service** | `8000` | Регистрация, JWT (RS256), роли, CRUD пользователей | Готов |
| **product_service** | `8001` | Категории и товары, фильтры, soft delete, RPC к user | Готов |
| **cart_service** | `8002` | Корзина в Redis | Есть код, в Compose пока отключён |
| **order_service** | — | Оформление заказов | Заготовка |

**Инфраструктура:** PostgreSQL (отдельные БД для user и product), RabbitMQ (AMQP + Management UI), Redis (для корзины и кэша catalog).

```
Клиент (HTTP)
    ├─► user_service  ──► Postgres (users)
    │         ▲
    │         │ RabbitMQ RPC: проверка seller
    │         │
    └─► product_service ──► Postgres (products)
              │
              │ (планируется) события Product.*
              ▼
         cart_service ──► Redis
```

---

## Сильные стороны

1. **Разделение ответственности** — у каждого сервиса свой домен и своя БД; проще масштабировать и развивать независимо.
2. **Production-minded user_service** — JWT RS256, refresh-токены, RBAC (`admin` / `user` / `seller`), healthcheck, структурированные логи, seed-скрипт, unit/integration-тесты.
3. **Каталог с «боевыми» деталями** — иерархия категорий, пагинация и фильтры, soft/hard delete, OpenAPI-описания, опциональный Redis-кэш.
4. **Асинхронная интеграция** — request/reply через RabbitMQ с `correlation_id` и таймаутами (маппинг в HTTP 504) — наглядный паттерн межсервисного вызова без жёсткой связки HTTP.
5. **DevOps-база** — Docker Compose с healthcheck и `depends_on`, разделение `.env` (Compose) и `.env.docker` (runtime), bind-mount + `--reload` для разработки.
6. **Современный Python-стек** — Python 3.12+, FastAPI, SQLAlchemy 2 async, Pydantic Settings, упаковка через **uv** (`pyproject.toml` + lockfile).

---

## Применённые паттерны и практики

| Паттерн / практика | Где проявляется |
|--------------------|-----------------|
| **Микросервисы + Database per service** | Отдельные Postgres для user и product |
| **Слоистая архитектура** | `api` → `services` → `repositories` → `storage` |
| **Dependency Injection** | FastAPI `Depends`, typed-зависимости (`AdminUserDep`, `SessionDep`, …) |
| **Repository** | Репозитории пользователей, товаров, категорий, корзины |
| **RPC / Messaging** | aio-pika, durable queue `user.get_user_by_id.seller` |
| **Кэширование** | Декоратор Redis-кэша в product_service (включается настройкой) |
| **RBAC** | Роли и dependency-guards на эндпоинтах |
| **Lifespan startup** | Проверка БД/MQ/Redis, миграции или `create_all`, фоновый consumer |
| **Middleware** | CORS, логирование запросов и медленных операций |
| **Healthchecks** | `/healthcheck` у сервисов + healthcheck контейнеров |
| **Soft delete** | Товары: режим `soft` / полное удаление |
| **Конфигурация** | Pydantic Settings, вложенные секции (app, postgres, rabbitmq, jwt, redis) |

---

## Быстрый старт

```bash
# из корня репозитория
docker compose up --build
```

| Что | URL |
|-----|-----|
| User API / Swagger | http://localhost:8000/docs |
| Product API / Swagger | http://localhost:8001/docs |
| RabbitMQ Management | http://localhost:15672 |

Остановка: `docker compose down`.

Полный чеклист (ключи JWT, env, миграции, seed, локальный запуск без Docker для приложений): см. **[deployment.md](./deployment.md)**.

---

## Стек

- **API:** FastAPI, Uvicorn  
- **БД:** PostgreSQL 16, SQLAlchemy 2 (asyncpg), Alembic (user_service)  
- **Кэш / корзина:** Redis  
- **Очереди:** RabbitMQ 3 (Management)  
- **Auth:** JWT RS256, OAuth2 password flow, bcrypt  
- **Логи:** Loguru  
- **Тесты:** pytest (+ asyncio)  
- **Упаковка / запуск:** uv, Docker, Docker Compose  

---

## Возможные пути развития

1. **Включить Redis и cart_service в Compose** — довести событие удаления товара → инвалидация/очистка позиций корзины; унифицировать типы ID (UUID vs int).
2. **Реализовать order_service** — checkout из корзины, статусы заказа, резерв остатков; паттерн saga / transactional outbox.
3. **API Gateway / BFF** — единая точка входа, проверка JWT один раз, rate limiting, маршрутизация.
4. **Общая аутентификация между сервисами** — раздача public key / JWKS, Bearer на product/cart/order (сейчас JWT сосредоточен в user_service).
5. **Миграции для product (и order)** — Alembic вместо `create_all` на старте.
6. **Observability** — Prometheus-метрики, OpenTelemetry-трейсы, correlation id через HTTP и MQ.
7. **CI/CD** — прогон pytest, smoke healthcheck после `compose up`, нагрузочные сценарии на базе `seed_users`.
8. **Production Docker** — сборка через `uv sync`, без bind-mount и `--reload`; единая версия Python во всех образах.
9. **Recommendation service** — персональные и популярные рекомендации на основе просмотров/покупок (сейчас только идея в roadmap).
10. **Усиление безопасности** — секреты вне репозитория, ужесточение CORS, минимальный payload в JWT.

---

## Структура репозитория

```
fastApi_marketplace_project/
├── docker-compose.yml
├── .env                      # переменные для подстановки в Compose
├── deployment.md
└── services/
    ├── user_service/
    ├── product_service/
    ├── cart_service/
    └── order_service/
```

---

## Лицензия и вклад

Проект демонстрационный. Pull request’ы и предложения по доработке сервисов приветствуются.
