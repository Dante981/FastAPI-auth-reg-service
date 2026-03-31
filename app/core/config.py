'''
Загрузка переменных окружения .env

'''


from pydantic_settings import BaseSettings
from pydantic import ConfigDict



class Settings(BaseSettings):
    
    DATABASE_URL_ASYNC: str                 # URL подключения к PostgreSQL с asyncpg драйвером
    DATABASE_URL_ASYNC_TEST: str            # URL подключения к тестовой PostgreSQL с asyncpg драйвером

    DEBUG: bool
    DATABASE_URL_SYNC: str                  # URL подключения к PostgreSQL для Alembic
    POSTGRES_DB: str                        # Имя базы
    POSTGRES_USER: str                      # Пользователь базы
    POSTGRES_PASSWORD: str                  # Пароль базы
        
    DATABASE_URL_SYNC_TEST: str             # URL к тестовой подключения к PostgreSQL для Alembic
    POSTGRES_DB_TEST: str                   # Имя тестовой базы
    POSTGRES_USER_TEST: str                 # Пользователь тестовой базы
    POSTGRES_PASSWORD_TEST: str             # Пароль тестовой базы

    ALEMBIC_ENV: str                        # преключение режимов миграций prod - test

    SECRET_KEY: str                         # Секретный ключ для JWT токенов
    ALGORITHM: str                          # Алгоритм подписи JWT
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int        # Время жизни access токена в минутах
    REFRESH_TOKEN_EXPIRE_MINUTES: int       # Время жизни refresh токена в минутах
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False
    )

settings = Settings()