# Модели SQLAlchemy

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr

Base = declarative_base() # Базовый класс для всех моделей SQLAlchemy

class User(Base): # Модель пользователя для хранения в бд
    __tablename__ = 'users'
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class LoginAttempt(Base):  # Модель для логов попыток входа
    __tablename__ = 'login_attempts'
    id = Column(String, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    ip_address = Column(String, nullable=False)
    success = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))