# Эндпоинты для регистрации, авторизации и работы с пользователями

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import models, database, security

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=models.UserRead)
def register(user_create: models.UserCreate, db: Session = Depends(database.get_db)):
    # Проверяем, существует ли пользователь с таким email
    existing_user = db.query(models.User).filter(models.User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    # Хэшируем пароль
    password_hash = security.get_password_hash(user_create.password)
    
    # Создаем нового пользователя
    new_user = models.User(
        id=security.generate_uuid(),
        email=user_create.email,
        password_hash=password_hash
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=models.UserRead)
def login(user_create: models.UserCreate, db: Session = Depends(database.get_db)):
    # Ищем пользователя по email
    user = db.query(models.User).filter(models.User.email == user_create.email).first()
    if not user or not security.verify_password(user_create.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    
    return user