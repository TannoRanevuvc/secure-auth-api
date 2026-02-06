# Эндпоинты для регистрации, авторизации и работы с пользователями

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app import models, database, security, schemas
from jose import jwt
from datetime import datetime, timedelta, timezone
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from fastapi import status
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
TIME_WINDOW_MINUTES = int(os.getenv("TIME_WINDOW_MINUTES"))
USER_LOGIN_ATTEMPT_LIMIT = int(os.getenv("USER_LOGIN_ATTEMPT_LIMIT"))

http_bearer = HTTPBearer()

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


def create_login_attempt(db: Session, email: str, ip_address: str, success: bool): # Логируем попытку входа
    attempt = models.LoginAttempt(
        id=security.generate_uuid(),
        email=email,
        ip_address=ip_address,
        success=success,
        created_at=datetime.now(timezone.utc)
    )
    db.add(attempt)
    db.commit()


def count_user_login_attempts(db: Session, ip_address: str, success: bool, time_window_minutes: int = TIME_WINDOW_MINUTES) -> int: # Считаем количество попыток входа
    time_threshold = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)
    return db.query(models.LoginAttempt).filter(
        models.LoginAttempt.ip_address == ip_address,
        models.LoginAttempt.success == success,
        models.LoginAttempt.created_at >= time_threshold
    ).count()


def clear_failed_login_attempts(db: Session,ip_address: str, success: bool, time_window_minutes: int = TIME_WINDOW_MINUTES): # Очищаем неудачные попытки входа
    time_threshold = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)
    db.query(models.LoginAttempt).filter(
        models.LoginAttempt.ip_address == ip_address,
        models.LoginAttempt.success == success,
        models.LoginAttempt.created_at >= time_threshold
    ).delete()
    db.commit()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(database.get_db)
): # Получаем текущего пользователя по JWT токену
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный токен")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный токен")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return user


@router.post("/register", response_model=schemas.UserRead)
def register(user_create: schemas.UserCreate, db: Session = Depends(database.get_db)):
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


@router.post("/login")
def login(user_create: schemas.UserCreate, db: Session = Depends(database.get_db), request: Request = None):
    ip_address = request.client.host if request and request.client else "unknown"
    if count_user_login_attempts(db, ip_address, success=False) >= USER_LOGIN_ATTEMPT_LIMIT:
        raise HTTPException(status_code=429, detail="Слишком много попыток входа. Попробуйте позже.")
    
    user = db.query(models.User).filter(models.User.email == user_create.email).first()
    if not user or not security.verify_password(user_create.password, user.password_hash):
        create_login_attempt(db, user_create.email, ip_address, False)
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    # Генерируем JWT access token
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user.id,
        "exp": expire
    }
    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    clear_failed_login_attempts(db, ip_address, success=False)
    create_login_attempt(db, user_create.email, ip_address, True)
    return JSONResponse({"access_token": access_token, "token_type": "bearer"})


@router.get("/me", response_model=schemas.UserRead)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user