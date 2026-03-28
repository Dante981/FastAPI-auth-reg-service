from datetime import datetime

from sqlalchemy import String, Integer, DateTime, func, ForeignKey, Boolean
from sqlalchemy.orm  import Mapped, mapped_column, relationship

from app.database import Base



class RefreshSession(Base):
    __tablename__ = "refresh_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    jti: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    device_info: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="sessions"
    )
