from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sqlalchemy import select, update

from app.schemas.roles import RoleCreate, RoleUpdate, RoleRead
from app.models.roles import Role
from app.models.users import User
from app.models.permissions import Permission






async def get_all_roles(db: AsyncSession) -> list[Role]:
    stmt = select(Role).options(selectinload(Role.permissions))
    result = await db.execute(stmt)
    return result.scalars().all()





async def get_role_by_user_id(user_id: int, db: AsyncSession) -> Role:
    stmt = (
        select(Role)
        .join(User, User.role_id == Role.id)
        .where(User.id == user_id)
        .options(selectinload(Role.permissions))
    )
    result = await db.execute(stmt)
    role = result.scalars().first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found for user",
        )
    return role


async def get_role_by_code(db: AsyncSession, role_code: str) -> Role:
   
    stmt = (
        select(Role)
        .options(selectinload(Role.permissions))
        .where(Role.code == role_code)
    )

    result = await db.execute(stmt)
    role = result.scalars().one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    return role

async def create_role(payload: RoleCreate, db: AsyncSession) -> Role:
    # Проверка уникальности
    existing_stmt = select(Role).where(
        (Role.code == payload.code) | (Role.name == payload.name)
    )
    existing = await db.execute(existing_stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role already exists",
        )

    # Загрузка разрешений
    permissions = []
    if payload.permission_codes:
        perms_stmt = select(Permission).where(
            Permission.code.in_(payload.permission_codes)
        )
        perms_result = await db.execute(perms_stmt)
        permissions = perms_result.scalars().all()

        found_codes = {perm.code for perm in permissions}
        missing_codes = set(payload.permission_codes) - found_codes
        if missing_codes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permissions not found: {', '.join(sorted(missing_codes))}",
            )

    # Создание роли
    role = Role(name=payload.name, code=payload.code, permissions=permissions)
    db.add(role)
    await db.commit()
    await db.refresh(role, attribute_names=["permissions"])
    return role



async def update_role_by_code(payload: RoleUpdate, role_code: str, db: AsyncSession) -> Role:
    role = await get_role_by_code(db, role_code)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    
    if payload.name and payload.name != role.name:
        conflict = await db.scalar(
            select(Role.id).where(Role.name == payload.name)
        )
        if conflict:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role name already exists")
        role.name = payload.name

    
    if payload.permission_codes is not None:
        permissions = []
        if payload.permission_codes:
            perms_result = await db.execute(
                select(Permission).where(Permission.code.in_(payload.permission_codes))
            )
            permissions = perms_result.scalars().all()
            found_codes = {perm.code for perm in permissions}
            missing_codes = set(payload.permission_codes) - found_codes
            if missing_codes:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Permissions not found: {', '.join(sorted(missing_codes))}",
                )
        role.permissions = permissions

    await db.commit()
    await db.refresh(role, attribute_names=["permissions"])
    return role


async def set_role_by_user_id_and_role_code(user_id: int, role_code: str, db: AsyncSession) -> User:

    new_role = await get_role_by_code(db, role_code)

    if not new_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    user_stmt = (
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .where(User.id == user_id)
    )
    result = await db.execute(user_stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    

    if user.role_id == new_role.id:
        return user

    try:
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(role_id=new_role.id)
        )
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user role: {str(e)}"
        )

    updated_user_stmt = (
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .where(User.id == user_id)
    )
    updated_result = await db.execute(updated_user_stmt)
    return updated_result.scalars().one()

