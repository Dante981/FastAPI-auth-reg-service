from fastapi import FastAPI
from app.routers import auth, users, roles, permissions


app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)







# Корневой эндпоинт
@app.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API"}