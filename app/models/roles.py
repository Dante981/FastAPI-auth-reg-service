from datetime import datetime

from sqlalchemy import String, Integer, DateTime, func, ForeignKey, Boolean
from sqlalchemy.orm  import Mapped, mapped_column, relationship

from app.database import Base


class Role(Base):
    __tablename__="roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True) 
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="role"
    )

    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
    )


