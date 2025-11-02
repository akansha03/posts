
from fastapi.testclient import TestClient
from app.main import app
from app import schema
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.database import get_db, Base
import pytest
from app.oauth2 import create_access_token
from alembic import command
from app import models

# refer the testing database

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
# To work with the database, use session local - sqlalchemy

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def session():
    # Below code is using SQLAlchemy to create tables based on the models - drop the table first and then create a new one so that it's all reset
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close() 

@pytest.fixture()
def client(session):
    # create using alembic
    #command.upgrade("head")
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    #command.downgrade("base")

@pytest.fixture
def test_user_2(client):
    user_data = {"email": "akansha.saraswat9@gmail.com", "password" : "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture
def test_user(client):
    user_data = {"email": "akansha.saraswat3@gmail.com", "password" : "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})

@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers, 
        "Authorization" : f"Bearer {token}"
    }
    return client

@pytest.fixture
def test_create_posts(test_user, session, test_user_2):
    posts_data = [{
        "title" : "first title",
        "content" : "first content",
        "owner_id" : test_user['id']
    }, 
    {
        "title" : "second title",
        "content" : "second content",
        "owner_id" : test_user['id']
    }, 
    {
        "title" : "third title",
        "content" : "third content",
        "owner_id" : test_user_2['id']
    }]

    def create_post_model(post):
        return models.Post(**post)

    post_map = map(create_post_model, posts_data)    
    posts = list(post_map)

    session.add_all(posts)
    #session.add_all([models.Post(title = "first title", content = "first content",  owner_id = test_user['id']),models.Post(title = "second title", content = "second content",  owner_id = test_user['id']),models.Post(title = "third title", content = "third content",  owner_id = test_user['id'])])
    
    session.commit()
    posts = session.query(models.Post).all()
    return posts
