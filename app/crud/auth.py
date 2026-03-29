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





async def user_register(user_create: UserCreate, db: AsyncSession) -> UserRead:
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

    return UserRead.model_validate(user)



async def user_login(form_data: UserLogin, db: AsyncSession) -> Token:
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

    