# Модели SQLAlchemy

from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel, EmailStr

Base = declarative_base() # Базовый класс для всех моделей SQLAlchemy

class User(Base): # Модель пользователя для хранения в бд
    __tablename__ = 'users'
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserCreate(BaseModel): # схема для создания юзера
    email: EmailStr
    password: str

class UserRead(BaseModel): # схема для чтения юзера (как будет отвечать апи)
    id: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True # позволяет пайдентик работать с орм