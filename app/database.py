'''
Base для всех моделей + engine

'''
from app.core.config import settings
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)



# Базовый класс для моделей БД
class Base(DeclarativeBase):
    pass


# Cоздаём асинхронный движок для PSQL
engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    echo=settings.DEBUG # Для логов SQL в проде False
)

# Фабрика сессий для пула соединений
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession, 
    expire_on_commit=False
)

# Dependency для FastAPI - предоставляет сессию БД в роутерах
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
