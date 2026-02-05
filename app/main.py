# Точка входа, запуск FastAPI
from fastapi import FastAPI
from app.api import users

app = FastAPI(title="Secure Auth API", description="API для безопасной регистрации и авторизации пользователей", version="1.0.0")

app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в Secure Auth API!"}

