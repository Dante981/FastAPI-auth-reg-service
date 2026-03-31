# FastAPI Auth & Registration Service

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red.svg)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-migrations-orange.svg)](https://alembic.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/Docker-blue.svg)](https://www.docker.com/)

Сервис авторизации и регистрации на FastAPI с асинхронной SQLAlchemy, JWT, refresh-сессиями и RBAC-модель доступа. 

## Содержание

- [Описание](#описание)
- [Возможности](#возможности)
- [Стек](#стек)
- [Структура проекта](#структура-проекта)
- [Схема данных](#схема-данных)
- [Роли и доступы](#роли-и-доступы)

## Описание

Асинхронный API на FastAPI для аутентификации, управления пользователями, ролями и permissions.
Проект реализует JWT-аутентификацию и RBAC-модель доступа, поддерживает регистрацию, вход, refresh токенов, logout, 
создание и обновление ролей, а также назначение ролей пользователям.


## Возможности

- Регистрация пользователя.
- Логин с JWT access/refresh token.
- Refresh token flow.
- Выход и отзыв refresh-сессии.
- Активные и неактивные пользователи через `is_active`.
- Система ролей RBAC `Permission`.
- Проверка доступа через `require_permission()`
- Pydantic-схемы для create/read/update.
- Alembic-миграции для схемы БД.
- Docker и Docker-Compose для контейнеризации(пока только PostgreSQL)

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
    - id
    - login
    - name
    - email
    - hashed_password
    - is_active
    - created_at
    - last_login_at
    - связь с roles(одна роль ко многим пользователям) по roles_id
    
### roles
    - id
    - code
    - name
    - created_at
    
### refresh_sessions
    - id
    - user_id
    - jti
    - revoked
    - expires_at
    - created_at
    - device_info
    - связь с users(один пользователь ко многим сессиям) по user_id


 ## Аутентификация

В проекте используется JWT-аутентификация.

### Регистрация

Пользователь указывает:
- login;
- name;
- email;
- password;
- password_confirm.

Если пароли не совпадают, API возвращает ошибку `400`.

### Вход

Логин выполняется по email и паролю.  
В ответ приходит access token.

### Refresh

Эндпоинт refresh выдаёт новый access token.  
В текущей архитектуре logout отзывает сессии, но access token может оставаться валидным до истечения срока жизни. Black list токенов(access token) не реализован.

### Logout

Logout отзывает сессии пользователя.  
Это блокирует дальнейший refresh через отозванную сессию.
 

## RBAC
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

#### Проверка доступа
```bash
def require_permission(permission: str):
    async def checker(current_user = Depends(get_current_user), db = Depends(get_db)):
        permissions = await get_user_permissions(current_user.id, db)
        if permission not in permissions:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user
    return checker
```
#### Использование:
```bash
@router.get("/", response_model=list[RoleRead], dependencies=[Depends(require_permission("roles:view"))])
async def get_roles(db: AsyncSession = Depends(get_db)) -> list[RoleRead]:
...
```

## Тестирование

Запуск тестов:

```bash
pytest
```
```bash
docker compose exec api pytest
```
Запуск с покрытием:

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
