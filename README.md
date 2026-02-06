# Secure Auth API

Масштабируемый и защищённый API-сервис для авторизации пользователей на FastAPI + PostgreSQL.

## Возможности
- Регистрация и авторизация пользователей
- Хеширование паролей (bcrypt)
- Валидация email (Pydantic)
- Работа с PostgreSQL через SQLAlchemy ORM
- Структурированный и расширяемый код

## Структура проекта
```
secure-auth-api/
│  .env
│  README.md
└─ app/
    │  main.py           # Точка входа FastAPI
    │  models.py         # Модели SQLAlchemy и схемы Pydantic
    │  database.py       # Подключение к БД и создание таблиц
    │  security.py       # Хеширование и проверка паролей
    └─ api/
        │  users.py      # Эндпоинты для пользователей
        │  ...
```

## Быстрый старт
1. Клонируйте репозиторий и перейдите в папку проекта.
2. Создайте и активируйте виртуальное окружение:
   ```sh
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```
3. Установите зависимости:
   ```sh
   pip install -r requirements.txt
   ```
4. Создайте файл `.env` в корне проекта.
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   SECRET_KEY=supersecretkey
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   TIME_WINDOW_MINUTES=10
   USER_LOGIN_ATTEMPT_LIMIT=5
   ```
5. Запустите сервер:
   ```sh
   .venv\Scripts\uvicorn.exe app.main:app --reload
   ```
6. Откройте документацию по API: http://127.0.0.1:8000/docs

## Зависимости
- fastapi
- uvicorn
- sqlalchemy
- psycopg2-binary
- python-dotenv
- bcrypt
- email-validator