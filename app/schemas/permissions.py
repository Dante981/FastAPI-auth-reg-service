from pydantic import BaseModel, Field, EmailStr, ConfigDict



class Permission(BaseModel):
    id: int = Field(..., gt=0, description="id")
    code: str = Field(..., max_length=100, description="Код")
    name: str = Field(..., max_length=100, description="Имя")


class PermissionRead(BaseModel):
    code: str = Field(..., max_length=100, description="Код")
    name: str = Field(..., max_length=100, description="Имя")

class PermissionCodeRead(BaseModel):
    code: str = Field(..., max_length=100, description="Код")