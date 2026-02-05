# Подключение к базе данных
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Автоматическое создание таблиц по моделям при запуске
models.Base.metadata.create_all(bind=engine)

def get_db():
    """Генератор для получения сессии базы данных."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
