from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    """
    Модель для создания пользователя
    Используется в POST эндпоинтах
    """
    login: str = Field(..., min_length=3, max_length=20, description="Логин")
    name: str = Field(..., min_length=2, max_length=20, description="Имя")
    email: EmailStr = Field(..., max_length=50, description="Email")
    password: str = Field(..., min_length=8, max_length=71, description="Пароль")
    password_confirm: str = Field(..., min_length=8, max_length=71)



class UserLogin(BaseModel):
    """
    Модель для авторизации пользователя
    Используется в POST эндпоинтах
    """
    email: EmailStr = Field(..., max_length=50, description="Email")
    password: str = Field(..., min_length=8, max_length=71, description="Пароль")




class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None


