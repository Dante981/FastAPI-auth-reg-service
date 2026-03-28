
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.database import get_db
from app.crud.users import update_user_profile

router = APIRouter(
    prefix="/users", 
    tags=["users"]
    )

#эндпоинт для получения профиля
@router.get("/me", response_model=UserRead)
async def read_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return current_user


#эндпоинт для обновления профиля
@router.patch("/me", response_model=UserRead)
async def update_me(new_data:UserUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> UserRead:
    return await update_user_profile(new_data=new_data, current_user=current_user, db=db)



#эндпоинт для мягкого удаления
@router.delete("/me", response_model=None)
async def soft_removal(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> None:
    pass