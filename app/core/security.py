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

from app.models.users import User
from app.models.RefreshSession import RefreshSession



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


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> UserReadAndRole:
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
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    stmt = (
        select(User, RefreshSession)
        .options(selectinload(User.role))
        .join(RefreshSession, RefreshSession.user_id == User.id)
        .where(
            User.id == user_id,
            User.is_active.is_(True),
            RefreshSession.jti == jti,
            RefreshSession.revoked.is_(False),
            RefreshSession.expires_at > now,
        )
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise exception

    return user


def require_role(*allowed_roles: str):
    def dependency(user: User = Depends(get_current_user)):
        if user.role.code not in allowed_roles:
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return user
    return dependency