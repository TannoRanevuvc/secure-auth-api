import pytest
from fastapi.testclient import TestClient
from app import create_app

def test_login(client):
    """Тест успешного входа с правильными учётными данными"""
    # регистрируем пользователя
    register_response = client.post('/users/register', json={
        'email': 'testuser@example.com',
        'password': 'testpassword123'
    })
    assert register_response.status_code == 200
    
    # логинимся
    response = client.post('/users/login', json={
        'email': 'testuser@example.com',
        'password': 'testpassword123'
    })
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'

def test_register(client):
    """Тест регистрации нового пользователя"""
    response = client.post('/users/register', json={
        'email': 'newuser@example.com',
        'password': 'newpassword123'
    })
    assert response.status_code == 200
    data = response.json()
    assert data['email'] == 'newuser@example.com'
    assert 'id' in data

def test_protected_route(client):
    """Тест доступа к защищённому роуту с правильным токеном"""
    # Регистрируем пользователя
    register_response = client.post('/users/register', json={
        'email': 'testuser@example.com',
        'password': 'testpassword123'
    })
    assert register_response.status_code == 200
    
    # Логинимся и получаем access token
    login_response = client.post('/users/login', json={
        'email': 'testuser@example.com',
        'password': 'testpassword123'
    })
    assert login_response.status_code == 200
    access_token = login_response.json()['access_token']

    # Обращаемся к защищённому роуту с токеном
    response = client.get('/users/me', headers={
        'Authorization': f'Bearer {access_token}'
    })
    assert response.status_code == 200
    data = response.json()
    assert data['email'] == 'testuser@example.com'

def test_protected_route_without_token(client):
    """Тест доступа к защищённому роуту без токена"""
    response = client.get('/users/me')
    assert response.status_code == 401

def test_protected_route_with_invalid_token(client):
    """Тест доступа с недействительным токеном"""
    response = client.get('/users/me', headers={
        'Authorization': 'Bearer invalidtoken123'
    })
    assert response.status_code == 401

def test_login_with_wrong_password(client):
    """Тест входа с неправильным паролем"""
    # регистрируем пользователя
    client.post('/users/register', json={
        'email': 'testuser@example.com',
        'password': 'correctpassword'
    })
    
    # залогинимся с неправильным паролем
    response = client.post('/users/login', json={
        'email': 'testuser@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401

def test_register_duplicate_email(client):
    """Тест регистрации с уже существующим email"""
    # регистрируем первого пользователя
    client.post('/users/register', json={
        'email': 'duplicate@example.com',
        'password': 'password123'
    })
    
    # пытаемся зарегистрировать с тем же email
    response = client.post('/users/register', json={
        'email': 'duplicate@example.com',
        'password': 'password456'
    })
    assert response.status_code == 400


def test_rate_limiting(client):
    """Тест ограничения количества попыток входа"""
    # регистрируем пользователя
    client.post('/users/register', json={
        'email': 'ratelimit@example.com',
        'password': 'password123'
    })

    # логинимся с неправильным паролем 5 раз
    for _ in range(5):
        response = client.post('/users/login', json={
            'email': 'ratelimit@example.com',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
    
    # На 6-ой попытке должно быть ограничение
    response = client.post('/users/login', json={
        'email': 'ratelimit@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 429

def test_cleanup_old_login_attempts(client):
    """Тест сброса лимита после успешного входа"""
    # регистрируем пользователя
    client.post('/users/register', json={
        'email': 'cleanup@example.com',
        'password': 'password123'
    })

    # логинимся с неправильным паролем 4 раза
    for _ in range(4):
        response = client.post('/users/login', json={
            'email': 'cleanup@example.com',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401

    # На 5-ой попытке всё ещё должно работать
    response = client.post('/users/login', json={
        'email': 'cleanup@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200

    # логинимся с неправильным паролем 5 раза
    for i in range(5):
        response = client.post('/users/login', json={
            'email': 'cleanup@example.com',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401

    # На 6-ой попытке должно быть ограничение
    response = client.post('/users/login', json={
        'email': 'cleanup@example.com',
        'password': 'password123'
    })
    assert response.status_code == 429