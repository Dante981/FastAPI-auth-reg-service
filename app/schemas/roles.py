from pydantic import BaseModel, Field, EmailStr, ConfigDict


class RoleBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., min_length=2, max_length=20, description="Имя")

class RoleCreate(RoleBase):
    """
    Модель для создания роли
    Используется в POST эндпоинтах
    """
    pass

class RoleReadPublic(RoleBase):
    """
    Модель для чтения роли
    Используется в публичных GET эндпоинтах
    """
    code: str = Field(..., description="Код роли")

class RoleRead(RoleReadPublic):
    """
    Модель для чтения роли
    Используется в GET эндпоинтах
    """
    id: int = Field(..., gt=0, description="ID роли")


