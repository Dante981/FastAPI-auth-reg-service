from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.models.roles import Role
from app.models.permissions import Permission
from app.schemas.permissions import PermissionCodeRead






async def get_user_permissions(user_id: int, db: AsyncSession) -> list[str]:
    stmt = (
        select(User)
        .options(
            selectinload(User.role).selectinload(Role.permissions)
        )
        .where(User.id == user_id)
    )

    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not user.role:
        return []

    return [perm.code for perm in user.role.permissions]
