
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.models.users import User
from app.schemas.user import UserRead, UserUpdate
from app.database import get_db
from app.crud.users import update_user_profile, soft_removal_user

router = APIRouter(
    prefix="/users", 
    tags=["users"]
    )

#Эндпоинт для получения профиля
@router.get("/me", response_model=UserRead)
async def read_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return current_user


#Эндпоинт для обновления профиля
@router.patch("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_me(new_data:UserUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> UserRead:
    return await update_user_profile(new_data=new_data, current_user=current_user, db=db)



#Эндпоинт для мягкого удаления
@router.delete("/me", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def soft_removal(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> None:
    await soft_removal_user(user_id=current_user.id, db=db)

