from datetime import datetime, timedelta, timezone

from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm 


from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from app.models.users import User
from app.schemas.auth import UserCreate, Token, UserLogin
from app.schemas.user import UserRead
from app.crud.session import create_session





async def user_register(user_create: UserCreate, db: AsyncSession) -> User:
    """
    Функция отвечает за регистрацию пользователя.

    Args:
        user_create (UserCreate): Данные нового пользователя.
            - login (str): Логин (3–20 символов).
            - name (str): Имя (2–20 символов).
            - email (EmailStr): Email (до 50 символов).
            - password (str): Пароль (8–71 символ).
            - password_confirm (str): Подтверждение пароля (должно совпадать с password).
        db (AsyncSession): Сессия для подключения к БД.

    Returns:
        User: Объект зарегистрированного пользователя с загруженной ролью.
            Содержит поля: id, login, email, name, created_at, role (загружена через selectinload).

    Raises:
        HTTPException (400): Если:
            - пароли не совпадают (detail="Пароли не совпадают");
            - пользователь с таким логином или email уже существует
              (detail="Пользователь с таким логином или email уже существует").

    Side effects:
        - Создаёт новую запись в таблице пользователей.
        - Сохраняет хешированный пароль (не исходный текст).

    Notes:
        - Пароль автоматически хешируется перед сохранением.
        - Проверка уникальности логина и email выполняется атомарно.
        - Роль пользователя назначается по умолчанию (логика в модели User).

    Example:
        >>> user_data = UserCreate(
        ...     login="john_doe",
        ...     name="John",
        ...     email="john@example.com",
        ...     password="secure123",
        ...     password_confirm="secure123"
        ... )
        >>> registered_user = await user_register(user_data, db_session)
    """
    if user_create.password != user_create.password_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пароли не совпадают")
    stmt = select(User).where(
        (User.login == user_create.login) | (User.email == user_create.email)
    )
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином или email уже существует"
        )

    user = User(
        login=user_create.login,
        email=user_create.email,
        name=user_create.name,
        hashed_password=hash_password(user_create.password)
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)


    stmt = (
    select(User)
    .options(selectinload(User.role))
    .where(User.id == user.id)
)
    result = await db.execute(stmt)
    user = result.scalar_one()

    return user



async def user_login(form_data: UserLogin, db: AsyncSession) -> Token:
    """
    Функция отвечает за аутентификацию пользователя и выдачу JWT‑токена.

    Args:
        form_data (UserLogin): Данные для авторизации.
            - email (EmailStr): Email пользователя (до 50 символов).
            - password (str): Пароль (8–71 символ).
        db (AsyncSession): Сессия для подключения к БД.

    Returns:
        Token: Объект с токеном доступа. Содержит:
            - access_token (str): JWT‑токен для авторизации.
            - token_type (str): Тип токена (всегда "bearer").

    Raises:
        HTTPException (401): Если:
            - пользователь с указанным email не найден ИЛИ неактивен
              (detail="Неверный email или пароль");
            - введённый пароль не соответствует сохранённому хешу
              (detail="Неверный email или пароль").

    Side effects:
        - Обновляет поле last_login_at у пользователя (время последнего входа).
        - Создаёт новую запись сессии в БД (через create_session).
        - Сохраняет изменения в БД (commit).

    Notes:
        - Аутентификация проходит в два этапа: проверка существования активного пользователя
          и верификация пароля.
        - Пароль проверяется через функцию verify_password (сравнение хешей).
        - Срок действия токена берётся из настроек (settings.ACCESS_TOKEN_EXPIRE_MINUTES).
        - Для каждого входа создаётся уникальная сессия (jti используется в токене).

    Example:
        >>> login_data = UserLogin(email="john@example.com", password="secure123")
        >>> token = await user_login(login_data, db_session)
        >>> print(token.access_token)
        # eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    stmt = select(User).where(
        User.email == form_data.email,
        User.is_active.is_(True))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    session = await create_session(user_id=user.id, db=db)
    access_token = create_access_token(data={"sub": str(user.id)}, jti=session.jti)
    return Token(access_token=access_token, token_type="bearer")

    