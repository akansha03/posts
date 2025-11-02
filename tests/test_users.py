from app import schema
import pytest
from jose import jwt
from app.config import settings


'''
def test_root(client):
    res = client.get("/")
    assert res.json().get('message') == 'Hello Akansha ! Adulting Sucks'
    assert res.status_code == 200
'''

def test_create_user(client):
    res = client.post("/users/", json={"email": "hello33@gmail.com", "password": "password123"})
    new_user = schema.UserOut(**res.json())
    assert new_user.email == "hello33@gmail.com"
    assert res.status_code == 201

def test_login_user(test_user, client):
    res = client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
    login_res = schema.Token(**res.json())

    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])
    
    id = payload.get("user_id")
    assert id == test_user['id']
    assert login_res.token_type == "bearer"
    assert res.status_code == 200

@pytest.mark.parametrize("email, password, status_code", [('akansha@gmail.com', 'password123', 403), ('hello33@gmail.com', 'password', 403), 
('hello133@gmail.com', 'password', 403), (None, 'password', 403), ('hello133@gmail.com', None, 403) ])
def test_incorrect_login_password(email, password, status_code, client):
    res = client.post("/login", data={"username": email, "password": password})
    assert res.status_code == status_code