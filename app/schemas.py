# Pydantic-схемы для валидации данных и сериализации/десериализации
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel): # схема для создания юзера
    email: EmailStr
    password: str

class UserRead(BaseModel): # схема для чтения юзера (как будет отвечать апи)
    id: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True # позволяет пайдентик работать с орм