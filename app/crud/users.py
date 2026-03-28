from sqlalchemy import select, or_
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserUpdate, UserRead
from app.models.user import User


async def update_user_profile(new_data: UserUpdate, current_user: User, db: AsyncSession) -> UserRead:
    data = new_data.model_dump(exclude_unset=True)

    conditions = []
    if "login" in data:
        conditions.append(User.login == data["login"])
    if "email" in data:
        conditions.append(User.email == data["email"])

    if conditions:
        stmt = select(User).where(or_(*conditions), User.id != current_user.id)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким логином или email уже существует",
            )
    
    for key, val in data.items():
        if val is not None:
            setattr(current_user, key, val)
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user