# Pydantic-схемы для валидации данных и сериализации/десериализации
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class UserCreate(BaseModel): # схема для создания юзера
    email: EmailStr
    password: str

class UserRead(BaseModel): # схема для чтения юзера (как будет отвечать апи)
    id: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) # позволяет пайдентик работать с орм