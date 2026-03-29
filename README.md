Структура
project/
├─ app/
│  ├─ main.py
│  ├─ models/
│  │  ├─ user.py
│  │  ├─ role.py
│  │  ├─ permission.py
│  │  └─ token.py
│  ├─ schemas/
│  │  ├─ user.py
│  │  ├─ auth.py
│  │  └─ permission.py
│  ├─ routers/
│  │  ├─ auth.py
│  │  ├─ users.py
│  │  ├─ permissions.py
│  │  └─ mock.py
│  ├─ crud/
│  │  ├─ user.py
│  │  ├─ role.py
│  │  ├─ permissions.py
│  ├─ core/
│  │  ├─ config.py
│  │  ├─ security.py
│  └─ database.py
├─ alembic/
├─ tests/
├─ docker-compose.yml
├─ Dockerfile
└─ README.md


Эндпоинты
Публичные авторизация auth:
    POST /auth/register — регистрация пользователя.
    POST /auth/login — вход по email и паролю, выдача access token.
    POST /auth/logout — выход из системы, инвалидизация сессии или refresh token.

Профиль пользователя:
    GET /users/me — получить свой профиль.
    PATCH /users/me — обновить свои данные.
    DELETE /users/me — мягко удалить свой аккаунт, установить is_active = false и разлогинить пользователя.

Админские права:
    GET /roles — список ролей.
    POST /roles — создать роль.
    PATCH /roles/{id} — изменить роль.
    DELETE /roles/{id} — удалить роль.

Управление пользователями:
    GET /users — список пользователей, только для администратора.
    GET /users/{id} — просмотр пользователя, если доступ разрешён.
    PATCH /users/{id} — админское обновление пользователя.
    DELETE /users/{id} — админское soft delete пользователя.

Фиктивные - для проверки ролей
    GET /mock/projects
    GET /mock/documents
    GET /mock/invoices



Тестовые пользователи##
test1@test.ru:1234567890:admin
test2@test.ru:1234567890:moderator
test3@test.ru:1234567890:user