from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.security import require_permission
from app.schemas.roles import RoleRead, RoleCreate, RoleUpdate, RoleSet
from app.schemas.user import UserRead

from app.crud.roles import get_all_roles, set_role_by_user_id_and_role_code, get_role_by_code, update_role_by_code, create_role



# Создаём маршрутизатор для управлением ролями
router = APIRouter(
    prefix="/roles",
    tags=["roles"]
)


#Эндпоинт получения роли пользователя по id (для админов)
@router.get("/users/{user_id}", response_model=RoleRead, dependencies=[Depends(require_permission("roles:view"))])
async def read_user_role(user_id: int, db: AsyncSession = Depends(get_db)) -> RoleRead:
    return await get_role_by_user_id(user_id=user_id, db=db)


#Эндпоинт для установки роли по code роли и id пользователя (для админов)
@router.patch("/users/{user_id}", response_model=UserRead, dependencies=[Depends(require_permission("users:assign_role"))])
async def set_user_role(user_id: int, role_code: RoleSet, db: AsyncSession = Depends(get_db)) -> UserRead:
    return await set_role_by_user_id_and_role_code(user_id=user_id, role_code=role_code.code, db=db)


#Эндпоинт получения списка ролей(для админов)
@router.get("/", response_model=list[RoleRead], dependencies=[Depends(require_permission("roles:view"))])
async def get_roles(db: AsyncSession = Depends(get_db)) -> list[RoleRead]:
    return await get_all_roles(db=db)


#Эндпоинт создания роли (для админов)
@router.post("/", response_model=RoleRead, status_code=201, dependencies=[Depends(require_permission("roles:create"))])
async def add_role(payload: RoleCreate, db: AsyncSession = Depends(get_db)) -> RoleRead:
    return await create_role(payload=payload, db=db)

#Эндпоинт получения роли по code(для админов)
@router.get("/{role_code}", response_model=RoleRead, dependencies=[Depends(require_permission("roles:view"))])
async def get_role(role_code:str, db: AsyncSession = Depends(get_db)) -> RoleRead:
    return await get_role_by_code(role_code=role_code, db=db)

#Эндпоинт обновления роли по code(для админов)
@router.patch("/{role_code}", response_model=RoleRead, dependencies=[Depends(require_permission("roles:update"))])
async def update_role(role_code:str, payload: RoleUpdate, db: AsyncSession = Depends(get_db)) -> RoleRead:
    return await update_role_by_code(payload=payload, role_code=role_code, db=db)


#Эндпоинт удаления роли по code(для админов)
@router.delete("/{role_code}", dependencies=[Depends(require_permission("roles:delete"))])
async def delete_role(role_code:str, db: AsyncSession = Depends(get_db)) -> None:
    pass


