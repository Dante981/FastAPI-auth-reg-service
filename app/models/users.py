"""
Модель пользователя

id - первичный ключ в БД [Integer]
email - email [String(50), un=True, null=False]
login - Логин [String(20), un=True, null=False]
hashed_password - Пароль(String(255))
name - Имя [String(20), null=False]

created_at - дата создания [DateTime, sv_default=func.now(), null=False]
last_login_at  - дата последнего захода [DateTime, def=None, null=True]

связи:
таблица roles - 

"""

from datetime import datetime

from sqlalchemy import String, Integer, DateTime, func, ForeignKey, Boolean
from sqlalchemy.orm  import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__="users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    login: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    name: Mapped[str] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default='true', nullable=False)


    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"),  default=2, unique=False, nullable=False)

    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="users"
    )

    sessions: Mapped[list["RefreshSession"]] = relationship(
        "RefreshSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )

