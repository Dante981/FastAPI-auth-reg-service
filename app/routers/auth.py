from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserRead
from app.schemas.auth import Token, UserCreate, UserLogin
from app.database import get_db
from app.crud.auth import user_register, user_login
from app.core.security import get_current_user

# Создаём маршрутизатор для авторизации
router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


#Эднпоинт регистрации
@router.post('/register', response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(create_user: UserCreate, db: AsyncSession = Depends(get_db)) -> UserRead:
    return await user_register(user_create=create_user, db=db)

#Эднпоинт входа
@router.post("/login", response_model=Token)
async def login_user(form_data: UserLogin, db: AsyncSession = Depends(get_db)) -> Token:
    return await user_login(form_data=form_data, db=db)

#Эднпоинт выхода
@router.post("/logout", status_code=204)
async def logout_user(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> None:
    pass

