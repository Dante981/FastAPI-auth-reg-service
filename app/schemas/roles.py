from pydantic import BaseModel, Field, ConfigDict
from app.schemas.permissions import PermissionRead


class RoleBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=2, max_length=20, description="Имя")
    code: str = Field(..., min_length=2, max_length=50, description="Код роли")


class RoleCreate(RoleBase):
    permission_codes: list[str] = Field(default_factory=list, description="Список кодов разрешений")


class RoleSet(BaseModel):
    code: str = Field(..., min_length=2, max_length=50, description="Код роли")

class RoleUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str | None = Field(default=None, min_length=2, max_length=20)
    permission_codes: list[str] | None = None


class RoleReadPublic(RoleBase):
    pass


class RoleRead(RoleBase):
    id: int = Field(..., gt=0, description="ID роли")
    permissions: list[PermissionRead] = Field(default_factory=list)