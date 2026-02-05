# Безопасность: хэширование паролей, генерация UUID и т.д.
import bcrypt
import uuid

def get_password_hash(password: str) -> str:
    """Хэширует пароль с помощью bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля и его хэша."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_uuid() -> str:
    """Генерирует уникальный UUID4."""
    return str(uuid.uuid4())