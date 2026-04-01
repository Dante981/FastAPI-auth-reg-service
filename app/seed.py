from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select, delete
from passlib.context import CryptContext
import asyncio
import sys



from app.core.config import settings
from app.models.roles import Role
from app.models.users import User
from app.crud.roles import get_role_by_code
from app.models.permissions import Permission, role_permissions




engine = create_async_engine(settings.DATABASE_URL_ASYNC, echo=False)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")



def hash_password(password: str) -> str:
    return pwd_context.hash(password)



async def seed_users(session: AsyncSession) -> None:
    user_role = await get_role_by_code(session, "user")
    admin_role = await get_role_by_code(session, "admin")
    moderator_role = await get_role_by_code(session, "moderator")

    users_to_create = [
        {
            "email": "test_user@test.ru",
            "login": "test1",
            "name": "test1",
            "role_id": user_role.id
        },
        {
            "email": "test_admin@test.ru",
            "login": "test2",
            "name": "test2",
            "role_id": admin_role.id
        },
        {
            "email": "test_moderator@test.ru",
            "login": "test3",
            "name": "test3",
            "role_id": moderator_role.id
        }
    ]

    for user_data in users_to_create:
        result = await session.execute(
            select(User).where(User.email == user_data["email"])
        )
        existing_user = result.scalar_one_or_none()

        if existing_user is None:
            session.add(User(
                email=user_data["email"],
                login=user_data["login"],
                name=user_data["name"],
                hashed_password=hash_password("1234567890"),
                role_id=user_data["role_id"]
            ))

    await session.commit()

async def seed_permissions(session: AsyncSession) -> None:
    permissions = [
        {"code": "users:view", "name": "View users"},
        {"code": "users:update", "name": "Update users"},
        {"code": "users:delete", "name": "Delete users"},
        {"code": "users:assign_role", "name": "Assign role to user"},
        {"code": "users:remove_role", "name": "Remove role from user"},
        {"code": "roles:view", "name": "View roles"},
        {"code": "roles:create", "name": "Create roles"},
        {"code": "roles:update", "name": "Update roles"},
        {"code": "roles:delete", "name": "Delete roles"},
        {"code": "sessions:view", "name": "View sessions"},
        {"code": "sessions:revoke", "name": "Revoke session"},
        {"code": "sessions:revoke_all", "name": "Revoke all sessions"},
    ]

    for perm_data in permissions:
        result = await session.execute(
            select(Permission).where(Permission.code == perm_data["code"])
        )
        perm = result.scalar_one_or_none()
        if perm is None:
            session.add(Permission(**perm_data))

    await session.commit()


async def seed_roles(session: AsyncSession) -> None:
    roles_data = [
        {"code": "user", "name": "User"},
        {"code": "admin", "name": "Administrator"},
        {"code": "moderator", "name": "Moderator"}
    ]

    for role_data in roles_data:
        result = await session.execute(
            select(Role).where(Role.code == role_data["code"])
        )
        existing_role = result.scalar_one_or_none()

        if existing_role is None:
            session.add(Role(**role_data))

    await session.commit()
async def seed_role_permissions(session: AsyncSession) -> None:
    role_codes = ["admin", "moderator", "user"]

    roles_result = await session.execute(
        select(Role).where(Role.code.in_(role_codes))
    )
    roles = {role.code: role for role in roles_result.scalars().all()}

    perms_result = await session.execute(select(Permission))
    perms = {perm.code: perm for perm in perms_result.scalars().all()}

    mapping = {
        "admin": list(perms.keys()),
        "moderator": [
            "users:view",
            "users:update",
            "roles:view",
            "sessions:view",
            "sessions:revoke",
        ],
        "user": [
            "users:view",
            "users:update",
            "sessions:view",
            "sessions:revoke",
        ],
    }

    role_ids = [role.id for role in roles.values()]
    if role_ids:
        await session.execute(
            delete(role_permissions).where(role_permissions.c.role_id.in_(role_ids))
        )

    await session.flush()

    for role_code, perm_codes in mapping.items():
        role = roles.get(role_code)
        if role is None:
            continue

        for code in perm_codes:
            perm = perms.get(code)
            if perm is None:
                continue

            await session.execute(
                role_permissions.insert().values(
                    role_id=role.id,
                    permission_id=perm.id,
                )
            )

    await session.commit()

async def run_seed() -> None:
    async with SessionLocal() as db:
        await seed_roles(db)  
        await seed_permissions(db)  
        await seed_role_permissions(db)  
        await seed_users(db)  


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "prod":
        asyncio.run(run_seed())
