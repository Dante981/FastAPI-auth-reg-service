'''
Загрузка переменных окружения .env

'''


from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    
    DATABASE_URL_ASYNC: str                 # URL подключения к PostgreSQL с asyncpg драйвером
    DEBUG: bool
    DATABASE_URL_SYNC: str                  # URL подключения к PostgreSQL для Alembic
    POSTGRES_DB: str                        # Имя базы
    POSTGRES_USER: str                      # Пользователь базы
    POSTGRES_PASSWORD: str                  # Пароль базы

    SECRET_KEY: str                         # Секретный ключ для JWT токенов
    ALGORITHM: str                          # Алгоритм подписи JWT
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int        # Время жизни access токена в минутах
    REFRESH_TOKEN_EXPIRE_MINUTES: int       # Время жизни refresh токена в минутах
    
    class Config:
        env_file = ".env"

settings = Settings()