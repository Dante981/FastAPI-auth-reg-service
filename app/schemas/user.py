from pydantic import BaseModel, Field, EmailStr

class UserUpdate(BaseModel):
    """
    Модель для обновления пользователя
    Используется в PUT/PATCH эндпоинтах
    """
    name: str | None = Field(default=None, min_length=2, max_length=20, description="Имя")
    login: str | None = Field(default=None, min_length=3, max_length=20, description="Логин")
    email: EmailStr | None  = Field(default=None, max_length=50, description="Email")
    



class UserRead(BaseModel):
    """
    Модель для чтения пользователя
    Используется в GET эндпоинтах
    """
    id: int = Field(..., gt=0, description="ID пользователя")
    login: str = Field(..., min_length=3, max_length=20, description="Логин")
    name: str = Field(..., min_length=2, max_length=20, description="Имя")
    email: EmailStr = Field(..., max_length=50, description="Email")
    is_active: bool = Field(default=True, description="Активность пользователя")

    model_config = {
        "from_attributes": True  # Включает поддержку ORM‑моделей
    }