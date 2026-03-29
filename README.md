# FastAPI Auth & Registration Service

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red.svg)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-migrations-orange.svg)](https://alembic.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/Docker-blue.svg)](https://www.docker.com/)

Сервис авторизации и регистрации на FastAPI с асинхронной SQLAlchemy, JWT, refresh-сессиями и системой ролей.

## Содержание

- [Описание](#описание)
- [Возможности](#возможности)
- [Стек](#стек)
- [Структура проекта](#структура-проекта)
- [Схема данных](#схема-данных)
- [Роли и доступы](#роли-и-доступы)

## Описание

Этот проект — API-сервис для регистрации, авторизации и управления доступом пользователей.

Он позволяет пользователю создать аккаунт, войти в систему, получать токены доступа и работать только с теми ресурсами, к которым у него есть права. После регистрации и входа сервер выдаёт JWT-токены, которые используются для подтверждения личности пользователя в следующих запросах.

В проекте используется JWT-аутентификация, refresh token flow, таблицы пользователей и ролей, а также dependency-based проверка прав доступа через `require_role()`.

JWT-аутентификация означает, что после входа пользователь получает подписанный токен, который передаётся в заголовке `Authorization`. Этот токен подтверждает, что запрос действительно отправил авторизованный пользователь.

Refresh token flow нужен для безопасного обновления access-токена без повторного ввода пароля. Access-токен живёт недолго, а refresh-токен используется для получения нового access-токена, когда старый истёк.

Таблица пользователей хранит основную информацию об аккаунте: логин, email, пароль в хэшированном виде, активность и роль. Таблица ролей нужна для разделения прав, например: обычный пользователь, администратор или модератор.

Проверка прав доступа построена через dependency `require_role()`. Это значит, что перед выполнением защищённого эндпоинта система сначала проверяет роль текущего пользователя. Если роль не подходит, сервер возвращает ошибку `403 Forbidden`, и доступ к действию запрещается.


## Возможности

- Регистрация пользователя.
- Логин с JWT access/refresh token.
- Refresh token flow.
- Выход и отзыв refresh-сессии.
- Активные и неактивные пользователи через `is_active`.
- Система ролей через `roles` и `users.role_id`.
- Проверка доступа через `require_role()`
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
    │   └── session.py
    ├── models/
    │   ├── __init__.py
    │   ├── users.py
    │   ├── roles.py
    │   └── refresh_sessions.py
    ├── routers/
    │   ├── auth.py
    │   ├── users.py
    │   ├── admins.py
    │   └── roles.py
    ├── schemas/
    │   ├── users.py
    │   ├── roles.py
    │   └── auth.py
    ├── __init__.py
    ├── database.py
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
    
### Роли и доступы
В проекте роль проверять по более стабильному **code** чем **id**.
#### Примеры:
    - admin — полный доступ.
    - user — обычный доступ.
    - moderator — ограниченный административный доступ.
#### Проверка роли
```text
def require_role(*allowed_roles: str):
    def dependency(user: User = Depends(get_current_user)):
        if user.role.code not in allowed_roles:
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return user
    return dependency
```
#### Использование:
```text
@router.post("/roles")
async def create_role(
    payload: RoleCreate,
    user: User = Depends(require_role("admin")),
):
...
```


