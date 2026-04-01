# FastAPI Auth & Registration Service

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red.svg)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-migrations-orange.svg)](https://alembic.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/Docker-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Сервис авторизации и регистрации на FastAPI с асинхронной SQLAlchemy, JWT, refresh-сессиями и RBAC-моделью доступа.

## Содержание

- [Описание](#описание)
- [Возможности](#возможности)
- [Стек](#стек)
- [Структура проекта](#структура-проекта)
- [Схема данных](#схема-данных)
- [Роли и доступы](#роли-и-доступы)
- [Аутентификация](#аутентификация)
- [Установка и запуск](#установка-и-запуск)
- [API](#api)
- [Тестирование](#тестирование)
- [Лицензия](#лицензия)

## Описание

Асинхронный API на FastAPI для аутентификации, управления пользователями, ролями и permissions. Проект реализует JWT-аутентификацию и RBAC-модель доступа, поддерживает регистрацию, вход, refresh токенов, logout, создание и обновление ролей, а также назначение ролей пользователям.

Для корректной работы рекомендуется сначала выполнить миграции Alembic, а затем заполнить таблицы начальными данными через `seed.py`.


## Возможности

- Регистрация пользователя.
- Логин с JWT access/refresh token.
- Refresh token flow.
- Выход и отзыв refresh-сессии.
- Активные и неактивные пользователи через `is_active`.
- Система ролей и permissions.
- Проверка доступа через `require_permission()`.
- Pydantic-схемы для create/read/update.
- Alembic-миграции для схемы БД.
- Docker и Docker Compose для контейнеризации.

## Стек

- Python 3.12+
- FastAPI
- SQLAlchemy 2.x async
- Alembic
- Pydantic v2
- PostgreSQL
- Docker
- Docker Compose
- pytest
- pytest-asyncio

## Структура проекта

```text
project/
└── app/
    ├── core/
    │   ├── config.py
    │   └── security.py
    ├── crud/
    │   ├── auth.py
    │   ├── roles.py
    │   ├── users.py
    │   ├── permissions.py
    │   └── session.py
    ├── models/
    │   ├── __init__.py
    │   ├── users.py
    │   ├── roles.py
    │   ├── permissions.py
    │   └── refresh_sessions.py
    ├── routers/
    │   ├── auth.py
    │   ├── users.py
    │   ├── permissions.py
    │   └── roles.py
    ├── schemas/
    │   ├── users.py
    │   ├── roles.py
    │   ├── permissions.py
    │   └── auth.py
    ├── __init__.py
    ├── database.py
    ├── seed.py
    └── main.py
alembic/
tests/
alembic.ini
docker-compose.yml
Dockerfile
requirements.txt
.gitignore
README.md
```

## Схема данных

### users

- `id`
- `login`
- `name`
- `email`
- `hashed_password`
- `is_active`
- `created_at`
- `last_login_at`
- связь с `roles` по `role_id`

### roles

- `id`
- `code`
- `name`
- `created_at`

### refresh_sessions

- `id`
- `jti`
- `revoked`
- `expires_at`
- `created_at`
- `device_info`
- связь с `users` по `user_id`

### permissions

- `id`
- `code`
- `name`

### role_permissions

Таблица связи «многие-ко-многим» между `roles` и `permissions`.

- `role_id`
- `permission_id`

## Роли и доступы

Проект использует ролевую модель доступа:

- `Role` — роль пользователя.
- `Permission` — отдельное право доступа.
- `Role.permissions` — список permissions, привязанных к роли.
- `User.role_id` — ссылка пользователя на роль.

### Логика ролей

- Роль можно создать с набором `permission_codes`.
- Если передан неизвестный permission code, API возвращает `404`.
- Если роль с таким `name` или `code` уже существует, API возвращает `409`.
- Роль можно назначить пользователю по коду роли.

### Проверка доступа

```python
def require_permission(permission: str):
    async def checker(current_user = Depends(get_current_user), db = Depends(get_db)):
        permissions = await get_user_permissions(current_user.id, db)
        if permission not in permissions:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user
    return checker
```

### Использование

```python
@router.get(
    "/",
    response_model=list[RoleRead],
    dependencies=[Depends(require_permission("roles:view"))],
)
async def get_roles(db: AsyncSession = Depends(get_db)) -> list[RoleRead]:
    ...
```

## Аутентификация

В проекте используется JWT-аутентификация.

### Регистрация

Пользователь указывает:

- `login`
- `name`
- `email`
- `password`
- `password_confirm`

Если пароли не совпадают, API возвращает ошибку `400`.

### Вход

Логин выполняется по email и паролю. В ответ приходит access token.

### Refresh

Эндпоинт refresh выдаёт новый access token.  
В текущей архитектуре logout отзывает сессии, но access token может оставаться валидным до истечения срока жизни. Black list для access token не реализован.

### Logout

Logout отзывает сессии пользователя. Это блокирует дальнейший refresh через отозванную сессию.

## Установка и запуск

### Локальная установка

```bash
git clone <repo-url>
cd <project-folder>
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Переменные окружения

Пример `.env`:

```env
# База данных
DATABASE_URL_ASYNC=postgresql+asyncpg://postgres:postgres@localhost:5432/app_db
DEBUG=True
POSTGRES_DB=AhRgS
POSTGRES_USER=postgres
POSTGRES_PASSWORD=vl7yDzjO2


# тестова База данных
DATABASE_URL_ASYNC_TEST=postgresql+asyncpg://postgres:postgres@localhost:5432/app_db_test
POSTGRES_DB_TEST=AhRgS_test
POSTGRES_USER_TEST=postgres
POSTGRES_PASSWORD_TEST=vl7yDzjO2

# Sync для Alembic миграций
DATABASE_URL_SYNC=postgresql+psycopg://postgres:postgres@localhost:5432/app_db
DATABASE_URL_SYNC_TEST=postgresql+psycopg://postgres:postgres@localhost:5432/app_db_test
ALEMBIC_ENV=prod

# JWT секрет (генерируйте свой!)
SECRET_KEY=change_me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10
REFRESH_TOKEN_EXPIRE_MINUTES=1440
```

### Миграции

```bash
alembic upgrade head
```

### Заполнение начальными данными

После миграций можно заполнить БД seed-данными:

```bash
python seed.py prod
```
```bash
docker compose exec api python -m app.seed prod
```
### Запуск приложения

```bash
uvicorn app.main:app --reload
```

### Запуск через Docker

```bash
docker compose up --build
```

## API

### Auth

#### `POST /auth/register`

Регистрация пользователя.

```json
{
  "login": "test_user",
  "name": "Test User",
  "email": "test@example.com",
  "password": "1234567890",
  "password_confirm": "1234567890"
}
```

#### `POST /auth/login`

Авторизация пользователя.

```json
{
  "email": "test@example.com",
  "password": "1234567890"
}
```

Ответ:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

#### `POST /auth/refresh`

Обновление access token.

Требует Bearer token.

#### `POST /auth/logout`

Выход пользователя.

Требует Bearer token. Отзывает refresh-сессии.

---

### Roles

#### `GET /roles/`

Получить список всех ролей.

#### `GET /roles/{role_code}`

Получить роль по коду.

#### `POST /roles/`

Создать новую роль.

```json
{
  "name": "Support",
  "code": "support",
  "permission_codes": [
    "users:view",
    "sessions:view"
  ]
}
```

#### `PATCH /roles/{role_code}`

Обновить роль.

Поддерживаемые изменения:

- `name`
- `permission_codes`

#### `DELETE /roles/{role_code}`

Если реализован, удаляет роль.

---

### Users

#### `GET /roles/users/{user_id}`

Получить роль пользователя по `user_id`.

#### `PATCH /roles/users/{user_id}`

Назначить пользователю роль.

```json
{
  "role_code": "moderator"
}
```

## Примеры `curl`

### Регистрация

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "login": "admin",
    "name": "Admin User",
    "email": "admin@example.com",
    "password": "1234567890",
    "password_confirm": "1234567890"
  }'
```

### Вход

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "1234567890"
  }'
```

### Создание роли

```bash
curl -X POST http://localhost:8000/roles/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "name": "Support",
    "code": "support",
    "permission_codes": ["users:view", "sessions:view"]
  }'
```

### Назначение роли пользователю

```bash
curl -X PATCH http://localhost:8000/roles/users/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "role_code": "moderator"
  }'
```

## Тестирование

### Запуск тестов

```bash
pytest
```

```bash
docker compose exec api pytest
```

### Запуск с покрытием

```bash
pytest --cov=app --cov-report=term-missing
```

```bash
docker compose exec api pytest --cov
```

## Что покрывают тесты

- регистрация;
- вход;
- refresh;
- logout;
- создание роли;
- дубликаты `name` и `code`;
- отсутствие permissions;
- доступ без токена;
- доступ с невалидным токеном;
- получение роли по коду;
- получение всех ролей;
- обновление роли;
- назначение роли пользователю;
- ошибки `404`, `403`, `409`.

## Лицензия

MIT