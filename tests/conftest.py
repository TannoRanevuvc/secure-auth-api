import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.models import Base
from app import create_app, database

# Добавляем родительскую директорию в sys.path, чтобы импорты работали корректно
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(scope="function")
def db():
    """Создает in-memory SQLite базу данных для каждого теста."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Используем StaticPool для in-memory БД, чтобы все соединения использовали одну и ту же БД

    )
    
    # Создаём таблицы
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Очищаем после тестаЫ
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def app(db):
    """Создает приложение FastAPI с тестовой базой данных."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db)
    
    app = create_app()
    
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    app.dependency_overrides[database.get_db] = override_get_db
    
    return app

@pytest.fixture
def client(app):
    """Создает TestClient для приложения."""
    return TestClient(app)

