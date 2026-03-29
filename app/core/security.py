from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from uuid import uuid4
from jose import jwt, JWTError

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from passlib.context import CryptContext

from app.core.config import settings
from app.database import get_db

from app.schemas.auth import Token
from app.models.users import User
from app.models.refresh_sessions import RefreshSession
from app.schemas.user import UserRead

from app.crud.session import create_session


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")    

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_jti() -> str:
    return str(uuid4())

def create_access_token(data: dict, jti: str, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    to_encode.update({
        "exp": expire,
        "jti": jti})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def  jwt_decode(token: str) -> dict:
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Could not validate credentials", 
        headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        user_id = payload.get("sub")
        jti = payload.get('jti')
        
        if user_id is None or jti is None:
            raise exception
        user_id = int(user_id)
        jti = str(jti)
    except (JWTError, ValueError):
        raise exception
    return {"user_id":user_id,"jti":jti}



async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> UserRead:

    payload = jwt_decode(token=token)
    user_id = int(payload.get("user_id"))
    jti = str(payload.get("jti"))

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    stmt = (
        select(User, RefreshSession)
        .options(selectinload(User.role))
        .join(RefreshSession, RefreshSession.user_id == User.id)
        .where(
            User.id == user_id,
            User.is_active.is_(True),
        )
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Could not validate credentials", 
        headers={"WWW-Authenticate": "Bearer"})

    return user

async def refresh_token(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> Token:
    payload = jwt_decode(token=token)
    user_id = int(payload.get("user_id"))
    jti = str(payload.get("jti"))

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    stmt = select(RefreshSession).where(
        RefreshSession.jti == jti,
        RefreshSession.user_id == user_id,
        RefreshSession.revoked.is_(False),
        RefreshSession.expires_at > now,
    )

    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    session.revoked = True
    await db.commit()

    new_session = await create_session(user_id=user_id, db=db)
    new_access_token = create_access_token(
        data={"sub": str(user_id)},
        jti=new_session.jti,
    )
    return Token(access_token=new_access_token, token_type="bearer")

async def get_session_by_jti(db: AsyncSession, jti: str) -> RefreshSession | None:
    stmt = select(RefreshSession).where(RefreshSession.jti == jti)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

def require_role(*allowed_roles: str):
    def dependency(user: User = Depends(get_current_user)):
        if user.role.code not in allowed_roles:
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return user
    return dependency