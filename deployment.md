# Инструкция по запуску и развёртыванию

Документ описывает, как поднять FastAPI Marketplace локально через Docker Compose и (опционально) запустить сервисы с хоста.

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

Если файла нет — скопируйте настройки из существующего примера в репозитории (.env.example).

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
| `user_service` | API пользователей и auth | **8000** |
| `product_service` | API товаров и категорий | **8001** |

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

Отдельного Alembic пока нет: таблицы создаются при lifespan-старте (`create_tables`).

---

## 5. Основные API (кратко)

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

## 6. Локальный запуск приложений без Docker (приложение на хосте)

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

## 7. Тесты

```bash
cd services/user_service
uv run pytest
# или: pytest

cd services/product_service
uv run pytest
```

Для интеграционных тестов нужны корректные `.env.test` и поднятая инфраструктура.

---

## 8. Типичные проблемы

| Симптом | Что проверить |
|---------|----------------|
| Сервис не стартует | Логи: `docker compose logs -f user_service` / `product_service` |
| Ошибка БД | Health Postgres, логин/пароль/имя БД в корневом `.env` и `.env.docker` |
| Ошибка RabbitMQ | Контейнер `rabbitmq` healthy; host в docker-env = `rabbitmq` |
| 401 / ошибки JWT | Наличие `jwt-private.pem` / `jwt-public.pem` и пути в настройках |
| Порт занят | Смените `*_EXTERNAL_PORT` в корневом `.env` |
| Healthcheck flaky | У сервисов большой `interval`; смотрите `/healthcheck` вручную через curl |

---

## 9. Рекомендации

- Убрать bind-mount исходников и флаг `--reload`; задать фиксированное число workers.  
- Собирать зависимости через `uv sync --frozen` в Dockerfile.  
- Секреты (пароли БД, JWT) — через Docker secrets / CI variables, не коммитить реальные `.env`.  
- Добавить reverse-proxy (Nginx / Traefik / API Gateway) перед сервисами.  
- Включить метрики и централизованные логи перед выкладкой на сервер.
