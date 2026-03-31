from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.security import require_permission
from app.schemas.roles import RoleRead, RoleCreate, RoleUpdate
from app.schemas.user import UserRead
from app.schemas.permissions import PermissionRead, PermissionCodeRead
from app.crud.permissions import get_user_permissions





# Создаём маршрутизатор для упровлением доступом
router = APIRouter(
    prefix="/permissions",
    tags=["permissions"]
)




#Эндпоинт получения permissions.code по user_id (для админов)
@router.get("/{user_id}", response_model=list[str])
async def get_roles(user_id: int, db: AsyncSession = Depends(get_db)) -> list[str]:
    return await get_user_permissions(user_id=user_id, db=db)
