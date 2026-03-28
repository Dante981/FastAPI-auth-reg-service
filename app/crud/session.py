from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_jti
from app.models.RefreshSession import RefreshSession


async def create_session(user_id: int, db: AsyncSession, expires_delta: timedelta | None = None, device_info: str | None = None) -> RefreshSession:
    jti = create_jti()
    expires_at = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    session = RefreshSession(
        user_id=user_id,
        jti=jti,
        device_info=device_info,
        expires_at=expires_at,
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session



async def get_session_by_jti(db: AsyncSession, jti: str) -> RefreshSession | None:
    stmt = select(RefreshSession).where(RefreshSession.jti == jti)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()