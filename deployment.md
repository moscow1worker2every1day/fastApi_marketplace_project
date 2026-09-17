# Инструкция по запуску и развёртыванию

Документ описывает, как поднять FastAPI Marketplace локально через Docker Compose и (опционально) запустить сервисы с хоста. Обзор архитектуры и паттернов — в [README.md](./README.md).

---

## Требования

- [Docker](https://docs.docker.com/get-docker/) и Docker Compose v2
- (Опционально) Python **3.12+**, [uv](https://github.com/astral-sh/uv) — для локального запуска приложений без контейнеров
- (Опционально) OpenSSL — для генерации JWT-ключей user_service

---

## 1. Подготовка окружения

### 1.1. Корневой `.env`

В корне репозитория должен лежать файл `.env`. Compose подставляет из него `${VAR}` (порты, учётки Postgres/RabbitMQ, host/port приложений).

Типичные значения по умолчанию:

| Переменная | Назначение | Пример |
|------------|------------|--------|
| `USER_APP_EXTERNAL_PORT` | Внешний порт user_service | `8000` |
| `PRODUCT_APP_EXTERNAL_PORT` | Внешний порт product_service | `8001` |
| `CART_APP_EXTERNAL_PORT` | Порт cart (когда сервис включён) | `8002` |
| `USER_POSTGRES_PORT` | Postgres user на хосте | `5432` |
| `PRODUCT_POSTGRES_PORT` | Postgres product на хосте | `5434` |
| `RABBITMQ_USER` / `RABBITMQ_PASSWORD` | Учётка RabbitMQ | см. ваш `.env` |

Если файла нет — восстановите переменные по образцу `docker-compose.yml` и существующим `services/*/.env.docker`.

### 1.2. Runtime-конфиг сервисов

| Файл | Когда используется |
|------|--------------------|
| `services/<service>/.env.docker` | Контейнеры (хосты `postgres_user`, `postgres_product`, `rabbitmq`) |
| `services/<service>/.env` | Запуск uvicorn/pytest с хоста (`localhost`) |
| `services/<service>/.env.test` | Тесты (pytest) |

Перед первым запуском проверьте, что в `.env.docker` корректны параметры RabbitMQ, JWT-пути и имена БД.

### 1.3. JWT-ключи (user_service)

Ключи нужны для подписи и проверки access/refresh токенов (RS256).

```bash
cd services/user_service/keys

openssl genrsa -out jwt-private.pem 2048
openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
```

Пути к файлам должны совпадать с настройками в `.env` / `.env.docker` сервиса. В Docker-образе каталог `keys` копируется в контейнер.

---

## 2. Запуск через Docker Compose

Из **корня** проекта:

```bash
docker compose up --build
```

Фоновый режим:

```bash
docker compose up --build -d
```

Остановка (контейнеры + сеть; volumes с данными БД сохраняются):

```bash
docker compose down
```

Полная очистка с удалением volumes Postgres:

```bash
docker compose down -v
```

### Что поднимается сейчас

| Сервис Compose | Описание | Порты на хосте |
|----------------|----------|----------------|
| `postgres_user` | БД пользователей | `${USER_POSTGRES_PORT}:5432` (обычно **5432**) |
| `postgres_product` | БД каталога | `${PRODUCT_POSTGRES_PORT}:5432` (обычно **5434**) |
| `rabbitmq` | Брокер + Management UI | **5672**, **15672** |
| `redis` | Корзина / опциональный кэш | **6379** |
| `user_service` | API пользователей и auth | **8000** |
| `product_service` | API товаров и категорий | **8001** |
| `cart_service` | API корзины | **8002** |

**Нет в Compose:** `order_service` (только заготовка кода).

Старт приложений ждёт healthy Postgres и RabbitMQ (`depends_on` + healthcheck).

---

## 3. Проверка работоспособности

| Ресурс | URL |
|--------|-----|
| User Swagger | http://localhost:8000/docs |
| Product Swagger | http://localhost:8001/docs |
| User health | http://localhost:8000/healthcheck |
| Product health | http://localhost:8001/healthcheck |
| RabbitMQ UI | http://localhost:15672 |

Логин в Management UI — значения `RABBITMQ_USER` / `RABBITMQ_PASSWORD` из корневого `.env`.

Пример быстрой проверки health:

```bash
curl -fsS http://localhost:8000/healthcheck
curl -fsS http://localhost:8001/healthcheck
```

---

## 4. Миграции и схема БД

### user_service

При старте сервиса выполняется инициализация БД (Alembic `upgrade head` при наличии ревизий + создание таблиц). Ревизии в `alembic/versions/` могут ещё отсутствовать — в этом случае схема создаётся через SQLAlchemy `create_all`.

Ручной запуск миграций (внутри контейнера), если понадобится:

```bash
docker compose exec user_service alembic upgrade head
```

### product_service

При старте сервиса выполняется Alembic `upgrade head`, затем проверка схемы через SQLAlchemy `create_all` (как в user_service). Начальная ревизия: `categories` + `products`.

```bash
docker compose exec product_service alembic upgrade head
```

### order_service

Alembic и ORM-модели (`orders`, `order_items`) уже добавлены. Сервис пока не в Compose и не поднимает lifespan с БД — миграции запускаются вручную, когда появится Postgres:

```bash
cd services/order_service
alembic upgrade head
```

---

## 5. Seed пользователей (опционально)

После того как `user_service` отвечает на healthcheck:

```bash
docker compose exec user_service python -m scripts.seed_users
```

Дополнительные флаги смотрите в `services/user_service/scripts/`.

---

## 6. Основные API (кратко)

### user_service (`:8000`)

- `POST /auth/sign_up` — регистрация  
- `POST /auth/sign_in` — вход (OAuth2 password)  
- `POST /auth/refresh` — обновление токена  
- CRUD пользователей и `/users/account/my_account/`  
- `GET /healthcheck`

### product_service (`:8001`)

- CRUD `/products`, `/categories`  
- Удаление товара с режимом soft/hard (query `mode`)  
- При создании товара — RPC в user_service (роль seller)  
- `GET /healthcheck`

### cart_service (`:8002`, когда включён)

- Получение / добавление / изменение количества / удаление позиций / очистка корзины в Redis  

---

## 7. Локальный запуск приложений без Docker (приложение на хосте)

Инфраструктуру удобнее оставить в Compose:

```bash
docker compose up -d postgres_user postgres_product rabbitmq
```

Далее в каждом сервисе:

```bash
cd services/user_service   # или product_service
uv sync                    # или pip install -r requirements.txt
# убедитесь, что .env указывает на localhost и верные порты Postgres/RabbitMQ
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Важно:** порты в `.env` сервиса должны совпадать с пробросом из Compose (user Postgres часто `5432`, product — `5434`, RabbitMQ — `localhost:5672`). Несоответствие host/port — частая причина ошибок подключения при смешанном запуске.

---

## 8. Тесты

### Unit / integration (внутри сервиса)

```bash
cd services/user_service
uv run pytest
# или: pytest

cd services/product_service
uv run pytest
```

Для интеграционных тестов нужны корректные `.env.test` и поднятая инфраструктура.

### E2E (интеграция сервисов)

Корневой пакет `tests/e2e` бьёт по HTTP в user/product/cart и проверяет связку через RabbitMQ.

| Файл | Назначение |
|------|------------|
| `docker-compose.e2e.yml` | Overlay: без bind-mount/`--reload`, healthcheck каждые 5s, отдельные volume |
| `.env.e2e.example` | Порты Compose + URL для pytest |
| `tests/e2e/` | Фикстуры клиентов, wait-for-health, сценарии |
| `scripts/e2e/run.ps1` / `run.sh` | Поднять стек → pytest → `down -v` |

```bash
# полный цикл
.\scripts\e2e\run.ps1          # Windows
./scripts/e2e/run.sh           # Unix

# против уже запущенного стека
.\scripts\e2e\run.ps1 -SkipUp -SkipDown
uv sync
uv run pytest tests/e2e -m e2e
```

Перед первым запуском: JWT-ключи в `services/user_service/keys/` и `services/*/`.env.docker` как для обычного Compose.

---

## 9. Redis и cart_service

`redis` и `cart_service` уже описаны в `docker-compose.yml`. Проверьте:

1. `services/cart_service/.env.docker` (`REDIS_HOST=redis`, `MQ_PRODUCT_EXCHANGE` / `MQ_PRODUCT_ROUTING_KEY` согласованы с product).
2. При необходимости включите кэш в product (`REDIS_ENABLED` в `.env.docker`).
3. Пересоберите: `docker compose up --build`.

Корзина будет на порту **8002** (если не меняли `CART_APP_EXTERNAL_PORT`).

---

## 10. Типичные проблемы

| Симптом | Что проверить |
|---------|----------------|
| Сервис не стартует | Логи: `docker compose logs -f user_service` / `product_service` / `cart_service` |
| Ошибка БД | Health Postgres, логин/пароль/имя БД в корневом `.env` и `.env.docker` |
| Ошибка RabbitMQ | Контейнер `rabbitmq` healthy; host в docker-env = `rabbitmq` |
| 401 / ошибки JWT | Наличие `jwt-private.pem` / `jwt-public.pem` и пути в настройках |
| Порт занят | Смените `*_EXTERNAL_PORT` в корневом `.env` / `.env.e2e` |
| E2E timeout на health | `docker compose -p marketplace-e2e ps` и `logs`; увеличьте `E2E_HEALTH_TIMEOUT_SEC` |
| E2E: товар не уходит из корзины | Совпадение exchange/routing key product↔cart; логи consumer в `cart_service` |

---

## 11. Рекомендации

- Убрать bind-mount исходников и флаг `--reload`; задать фиксированное число workers.
- Собирать зависимости через `uv sync --frozen` в Dockerfile.
- Секреты (пароли БД, JWT) — через Docker secrets / CI variables, не коммитить реальные `.env`.
- Добавить reverse-proxy (Nginx / Traefik / API Gateway) перед сервисами.
- Включить метрики и централизованные логи перед выкладкой на сервер.
- В CI: `scripts/e2e/run.sh` после сборки образов.

Минимальный сценарий на VPS: Docker → клон репозитория → заполнить `.env` / `.env.docker` → JWT-ключи → `docker compose up -d --build` → health/Swagger за reverse-proxy с TLS.
